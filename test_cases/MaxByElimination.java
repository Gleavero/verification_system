public class MaxByElimination {

  public static int max(int[] a) {
    int x = 0;
    int y = a.length - 1;

    while (x != y) {
      if (a[x] <= a[y])
        x++;
      else
        y--;
    }
    return x;
  }
}
