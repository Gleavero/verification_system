// This example was written by Viktorio S. el Hakim - 1/2021
// It establishes that the array is sorted, but not that it is a permutation of the input array

public class BubbleSort {

  public static void sort(int[] arr) {
    for (int i = 0; i < arr.length; i++) {

      for (int j = arr.length - 1; j > i; j--) {
        if (arr[j - 1] < arr[j]) {
          int tmp = arr[j];
          arr[j] = arr[j - 1];
          arr[j - 1] = tmp;
        }
      }
    }
  }
}
