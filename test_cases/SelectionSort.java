// This example was written by Viktorio S. el Hakim - 1/2021
// It establishes that the array is sorted, but not that it is a permutation of the input array

public class SelectionSort {
  public static void sort(int /* @ non_null @ */ [] arr) {
    for (int i = 0; i < arr.length; i++) {
      int ub = arr[i];
      int l = i;

      for (int j = i + 1; j < arr.length; j++) {
        if (arr[j] > ub) {
          l = j;
          ub = arr[j];
        }
      }

      arr[l] = arr[i];
      arr[i] = ub;
    }
  }
}
