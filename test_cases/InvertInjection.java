public class InvertInjection {

  static public int N;
  static public int M;
  static public int[] a;
  static public int[] b;

  public void invert() {

    for (int k = 0; k < M; k++)
      b[k] = -1;

    for (int k = 0; k < N; k++) {
      b[a[k]] = k;
    }
  }
}
