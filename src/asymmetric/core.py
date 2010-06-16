from deferred import Deferred, defer
import traceback
import sys
import types

def mergeFunctionMetadata(f, g):
    """
    Overwrite C{g}'s name and docstring with values from C{f}.  Update
    C{g}'s instance dictionary with C{f}'s.

    To use this function safely you must use the return value. In Python 2.3,
    L{mergeFunctionMetadata} will create a new function. In later versions of
    Python, C{g} will be mutated and returned.

    @return: A function that has C{g}'s behavior and metadata merged from
        C{f}.
    """
    try:
        g.__name__ = f.__name__
    except TypeError:
        try:
            merged = new.function(
                g.func_code, g.func_globals,
                f.__name__, inspect.getargspec(g)[-1],
                g.func_closure)
        except TypeError:
            pass
    else:
        merged = g
    try:
        merged.__doc__ = f.__doc__
    except (TypeError, AttributeError):
        pass
    try:
        merged.__dict__.update(g.__dict__)
        merged.__dict__.update(f.__dict__)
    except (TypeError, AttributeError):
        pass
    merged.__module__ = f.__module__
    return merged

def _chain(to_gen, g, deferred):
    # This function is complicated by the need to prevent unbounded recursion
    # arising from repeatedly yielding immediately ready deferreds.  This while
    # loop and the state variable solve that by manually unfolding the
    # recursion.

    while True:
        #print to_gen, g, deferred
        try:
            # Send the last result back as the result of the yield expression.
            if isinstance(to_gen, Exception):
                from_gen = g.throw(type(to_gen), to_gen)
            #elif isinstance(to_gen, TwistedFailure):
            #    from_gen = to_gen.throwExceptionIntoGenerator(g)
            else:
                from_gen = g.send(to_gen)
        except StopIteration:
            # "return" statement (or fell off the end of the generator)
            from_gen = None
        except Exception, e:
            tb = traceback.format_exc()
            if not hasattr(e, "_tb"):
                e._tb = {'tracebacks': []}
            e._tb['tracebacks'].append(tb)
            deferred.callback(e)
            return deferred


        if not isinstance(from_gen, Deferred):
            deferred.callback(from_gen)
            return deferred

        state = {'waiting': True}

        # a deferred was yielded, get the result.
        def gotResult(r):
            if state['waiting']:
                state['waiting'] = False
                state['result'] = r
            else:
                _chain(r, g, deferred)

        from_gen.add_callback(gotResult)

        if state['waiting']:
            # Haven't called back yet, set flag so that we get reinvoked
            # and return from the loop
            state['waiting'] = False
            return deferred

        to_gen = state['result']


def maybeDeferredGenerator(f, *args, **kw):
    try:
        result = f(*args, **kw)
    except Exception, e:
        print e
        tb = traceback.format_exc()
        if not hasattr(e, "_tb"):
            e._tb = {'tracebacks': []}
        e._tb['tracebacks'].append(tb)
        
        return defer(e)
    
    if isinstance(result, types.GeneratorType):
        return _chain(None, result, Deferred())
    elif isinstance(result, Deferred):
        return result

    return defer(result)


def inline(f):
    def unwindGenerator(*args, **kwargs):
        return maybeDeferredGenerator(f, *args, **kwargs)
    return mergeFunctionMetadata(f, unwindGenerator)
