public class TwoSum {

  class Pair {
    int i;
    int j;

    Pair(int ii, int jj) {
      i = ii;
      j = jj;
    }
  }

  Pair twoLoop(int[] a, int sum) {
    for (int i = 0; i < a.length; i++) {
      for (int j = 0; j < a.length; j++) {
        if (a[i] + a[j] == sum)
          return new Pair(i, j);
      }
    }
    return null;
  }

  Pair oneLoopPositive(int[] a, int sum) {
    int[] seen = new int[sum + 1];
    for (int i = 0; i < a.length; i++) {
      if (a[i] <= sum) {
        seen[a[i]] = i + 1;
        int j = seen[sum - a[i]];
        if (j != 0)
          return new Pair(i, j - 1);
      }
    }
    return null;
  }
}
