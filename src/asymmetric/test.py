from asymmetric.core import *

@inline
def test1():
    #raise Exception("boo")
    yield "stuff"
    
@inline
def main():
    m = yield test1()
    print m

#if __name__ == "__main__":
main()
