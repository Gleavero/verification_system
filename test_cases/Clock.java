public class Clock {

  // The number of seconds in a minute.
  public static final int SECS_IN_MIN = 60;

  // The number of minutes in an hour.
  public static final int MINS_IN_HOUR = 60;

  // The number of hours in a day.
  public static final int HOURS_IN_DAY = 24;

  // Instance Fields

  /**
   * The current hours on the clock.
   */
  private int my_hours; // @ in hours;

  /**
   * The current minutes on the clock.
   */
  private int my_minutes; // @ in minutes;

  /**
   * The current seconds on the clock.
   */
  private int my_seconds; // @ in seconds;

  // model queries for legal times and total number of seconds on the clock

  // Constructor

  /*
   * the constructor should have appropriate constructs that force
   * the client to validate the data passed in.
   */

  /**
   * Constructs a new Clock set to the specified time.
   * 
   * @param the_hours   The initial setting for hours.
   * @param the_minutes The initial setting for minutes.
   * @param the_seconds The initial setting for seconds.
   */
  public Clock(final int the_hours, final int the_minutes, final int the_seconds) {
    my_hours = the_hours;
    my_minutes = the_minutes;
    my_seconds = the_seconds;
  }

  /**
   * @return The current hours on the clock.
   */
  public /* @ pure helper */ int hours() {
    return my_hours;
  }

  /**
   * @return The current minutes on the clock.
   */
  public /* @ pure helper */ int minutes() {
    return my_minutes;
  }

  /**
   * @return The current seconds on the clock.
   */
  public /* @ pure helper */ int seconds() {
    return my_seconds;
  }

  /**
   * Checks to see if the time on this clock is later than the time
   * on the specified Clock.
   * 
   * @param the_other_clock The other Clock to check.
   * @return true if this Clock has a later time, false otherwise.
   */
  public /* @ pure */ boolean later(final Clock the_other_clock) {
    return my_hours > the_other_clock.my_hours ||
        (my_hours == the_other_clock.my_hours &&
            my_minutes > the_other_clock.my_minutes)
        ||
        (my_hours == the_other_clock.my_hours &&
            my_minutes == the_other_clock.my_minutes &&
            my_seconds > the_other_clock.my_seconds);
  }

  /**
   * Checks to see if the time on this clock is earlier than the time
   * on the specified Clock.
   * 
   * @param the_other_clock The other Clock to check.
   * @return true if this Clock has an earlier time, false otherwise.
   */
  public /* @ pure */ boolean earlier(final Clock the_other_clock) {
    return my_hours < the_other_clock.my_hours ||
        (my_hours == the_other_clock.my_hours &&
            my_minutes < the_other_clock.my_minutes)
        ||
        (my_hours == the_other_clock.my_hours &&
            my_minutes == the_other_clock.my_minutes &&
            my_seconds < the_other_clock.my_seconds);
  }

  // Commands

  /**
   * Sets the hours on the clock.
   * 
   * @param the_hours The new value for hours.
   */
  protected void setHours(final int the_hours) {
    my_hours = the_hours;
  }

  /**
   * Sets the minutes on the clock.
   * 
   * @param the_minutes The new value for minutes.
   */
  protected void setMinutes(final int the_minutes) {
    my_minutes = the_minutes;
  }

  /**
   * Sets the seconds on the clock.
   * 
   * @param the_seconds The new value for seconds.
   */
  protected void setSeconds(final int the_seconds) {
    my_seconds = the_seconds;
  }

  /**
   * Ticks the clock forward by one second. If we have reached the
   * end of the day (that is, we tick forward from 23:59:59), the clock
   * should wrap around to 00:00:00.
   */
  public void tick() {
    my_seconds += 1;

    if (my_seconds >= SECS_IN_MIN) {
      my_minutes += 1;
      my_seconds = 0;
    }

    if (my_minutes >= MINS_IN_HOUR) {
      my_hours += 1;
      my_minutes = 0;
    }

    if (my_hours >= HOURS_IN_DAY) {
      my_hours = 0;
    }
  }
}
