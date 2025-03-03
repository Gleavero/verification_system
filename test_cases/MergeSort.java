// This example was written by Viktorio S. el Hakim - 1/2021
// It establishes that the array is sorted, but not that it is a permutation of the input array

import java.util.Arrays;

public class MergeSort {
  public static void sort(int[] arr) {
    if (arr.length > 0) {
      sortRec(arr, 0, arr.length);
    }
  }

  private static void sortRec(int[] arr, int l, int r) {
    if (l + 1 < r) {
      int mid = l + (r - l) / 2;
      sortRec(arr, l, mid);
      sortRec(arr, mid, r);
      merge(arr, l, mid, r);
    }
  }

  private static void merge(int /* @ non_null @ */ [] arr, final int l, final int m, final int r) {
    final int[] lCpy = Arrays.copyOfRange(arr, l, m),
        rCpy = Arrays.copyOfRange(arr, m, r);

    int l1 = 0, r1 = 0;
    for (int i = l; i < r; i++) {
      if (l1 < lCpy.length && (r1 >= rCpy.length || lCpy[l1] >= rCpy[r1])) {
        arr[i] = lCpy[l1++];
      } else {
        arr[i] = rCpy[r1++];
      }
    }
  }
}
