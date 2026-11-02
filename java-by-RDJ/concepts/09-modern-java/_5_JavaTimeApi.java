// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.time.DayOfWeek;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.Period;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalAdjusters;
import java.util.Locale;

public class _5_JavaTimeApi {

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHY java.time (Java 8) REPLACED Date AND Calendar
        // The old classes were mutable (not thread-safe), counted months from 0, counted years
        // from 1900, mixed "a date" with "a moment" and had confusing time-zone handling.
        // java.time types are IMMUTABLE (every change returns a NEW object), months are 1-12,
        // and each type says exactly what it represents. Use java.time in new code.
        // ============================================

        // ============================================
        // SECTION 2: THE MAIN TYPES - ONE PER IDEA
        //   LocalDate       a calendar date, no time, no zone      2026-03-01
        //   LocalTime       a clock time, no date, no zone         14:30
        //   LocalDateTime   date + time, still no zone             2026-03-01T14:30
        //   ZonedDateTime   date + time + time zone                2026-03-01T14:30-05:00[America/New_York]
        //   Instant         one exact moment on the timeline (UTC) used for timestamps
        // To keep this program's output identical on every run, we use fixed dates, not now().
        // ============================================

        LocalDate date = LocalDate.of(2026, 3, 1);
        LocalTime time = LocalTime.of(14, 30);
        LocalDateTime dateTime = LocalDateTime.of(date, time);
        System.out.println("LocalDate:     " + date + "  (" + date.getDayOfWeek() + ", day " + date.getDayOfYear() + " of the year)");
        System.out.println("LocalTime:     " + time);
        System.out.println("LocalDateTime: " + dateTime);
        // LocalDate.of(2026, 13, 1);                              // DateTimeException: month 13 is invalid
        // LocalDate.of(2026, 2, 30);                              // DateTimeException: no 30th of February

        try {
            LocalDate.of(2026, 2, 30);
        } catch (java.time.DateTimeException e) {
            System.out.println("invalid date rejected: " + e.getMessage());
        }
        System.out.println("LocalDate.now() exists too (today's date, different each day): "
                + (LocalDate.now() instanceof LocalDate));


        // ============================================
        // SECTION 3: IMMUTABLE - "CHANGING" GIVES A NEW OBJECT
        // ============================================

        LocalDate nextWeek = date.plusDays(7);
        System.out.println("original: " + date + ", plusDays(7): " + nextWeek + "   <- original untouched");
        date.plusDays(7);                                          // a classic bug: the result is thrown away, 'date' is unchanged

        System.out.println("plusMonths(1) from Jan 31, 2026: " + LocalDate.of(2026, 1, 31).plusMonths(1) + "   (clamped to the last valid day)");
        System.out.println("leap year 2028? " + LocalDate.of(2028, 1, 1).isLeapYear() + ", 2026? " + LocalDate.of(2026, 1, 1).isLeapYear());
        System.out.println("first Monday of March 2026: " + date.with(TemporalAdjusters.firstInMonth(DayOfWeek.MONDAY)));
        System.out.println("last day of that month:     " + date.with(TemporalAdjusters.lastDayOfMonth()));


        // ============================================
        // SECTION 4: Period vs Duration
        //   Period   = an amount in DATE units: years, months, days     (calendar-based)
        //   Duration = an amount in TIME units: hours, minutes, seconds (exact length of time)
        // ============================================

        Period age = Period.between(LocalDate.of(1990, 5, 20), LocalDate.of(2026, 3, 1));
        System.out.println("Period:   " + age + "  = " + age.getYears() + " years, " + age.getMonths() + " months, " + age.getDays() + " days");

        Duration shift = Duration.between(LocalTime.of(9, 15), LocalTime.of(17, 45));
        System.out.println("Duration: " + shift + "  = " + shift.toHours() + " h " + shift.toMinutesPart() + " min");

        long daysBetween = ChronoUnit.DAYS.between(LocalDate.of(2026, 1, 1), LocalDate.of(2026, 3, 1));
        System.out.println("ChronoUnit.DAYS.between Jan 1 and Mar 1 2026: " + daysBetween);


        // ============================================
        // SECTION 5: FORMATTING AND PARSING
        // DateTimeFormatter is immutable and thread-safe (the old SimpleDateFormat was not).
        // Patterns: yyyy year, MM month number, MMM short month name, dd day, HH 24-hour, hh 12-hour, mm minutes.
        // ============================================

        DateTimeFormatter pretty = DateTimeFormatter.ofPattern("EEEE, d MMMM yyyy 'at' HH:mm", Locale.ENGLISH);
        System.out.println("formatted: " + dateTime.format(pretty));
        System.out.println("ISO built-in: " + DateTimeFormatter.ISO_LOCAL_DATE.format(date));

        LocalDate parsed = LocalDate.parse("2026-12-25");          // the ISO format works with no formatter
        LocalDate parsedCustom = LocalDate.parse("25/12/2026", DateTimeFormatter.ofPattern("dd/MM/yyyy"));
        System.out.println("parsed ISO: " + parsed + ", parsed dd/MM/yyyy: " + parsedCustom + ", equal: " + parsed.equals(parsedCustom));
        try {
            LocalDate.parse("25/12/2026");                         // wrong format for the default parser
        } catch (DateTimeParseException e) {
            System.out.println("DateTimeParseException: " + e.getMessage());
        }
        // Mixing up "MM" (month) and "mm" (minutes) is a very common bug.


        // ============================================
        // SECTION 6: TIME ZONES
        // The same MOMENT is a different wall-clock time in different zones.
        // ============================================

        ZonedDateTime newYork = ZonedDateTime.of(LocalDateTime.of(2026, 7, 1, 9, 0), ZoneId.of("America/New_York"));
        ZonedDateTime tokyo = newYork.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
        ZonedDateTime utc = newYork.withZoneSameInstant(ZoneId.of("UTC"));
        System.out.println("New York: " + newYork);
        System.out.println("Tokyo:    " + tokyo + "   (same instant)");
        System.out.println("UTC:      " + utc);
        System.out.println("same instant? " + newYork.toInstant().equals(tokyo.toInstant()));

        // Daylight saving: 2:30 AM on 8 March 2026 does not exist in New York (clocks jump 2:00 -> 3:00)
        ZonedDateTime gap = ZonedDateTime.of(LocalDateTime.of(2026, 3, 8, 2, 30), ZoneId.of("America/New_York"));
        System.out.println("2:30 on the spring-forward day becomes: " + gap.toLocalTime());

        // Duration across the change is the REAL elapsed time
        ZonedDateTime before = ZonedDateTime.of(LocalDateTime.of(2026, 3, 8, 1, 0), ZoneId.of("America/New_York"));
        ZonedDateTime after = before.plusHours(2);
        System.out.println("1:00 plus 2 real hours on that day: " + after.toLocalTime());


        // ============================================
        // SECTION 7: Instant - FOR TIMESTAMPS
        // Store and send Instants (or UTC); convert to a zone only to DISPLAY to a person.
        // ============================================

        Instant epoch = Instant.ofEpochSecond(0);
        Instant later = epoch.plus(1, ChronoUnit.DAYS);
        System.out.println("Instant epoch: " + epoch + ", plus one day: " + later);
        System.out.println("seconds since epoch: " + later.getEpochSecond());


        // ============================================
        // SECTION 8: RULES TO REMEMBER
        // 1) Pick the type that says what you mean: LocalDate for a birthday, Instant for a log
        //    timestamp, ZonedDateTime for a meeting in a place.
        // 2) Everything is immutable: use the RETURN value.
        // 3) Period for calendar amounts, Duration for exact time.
        // 4) Store UTC / Instant; show local time at the edge.
        // 5) For testable code, pass a java.time.Clock instead of calling now() everywhere.
        // ============================================
    }
}
