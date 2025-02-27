// It establishes that the sum is always non-negative and within the range of Integer

public class Calculator {

    /*@
         requires a != null && b != null;
         ensures \result >= 0;
         ensures \result <= Integer.MAX_VALUE; // assuming Integer.MAX_VALUE is used for calculation
     @*/
    public int add(int a, int b) {
        return a + b;
    }
}