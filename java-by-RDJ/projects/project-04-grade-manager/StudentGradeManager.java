import java.util.Scanner;

// ============================================================
// PROJECT: STUDENT GRADE MANAGEMENT SYSTEM
// A console-based app that exercises every 01-basics concept:
// variables/data types, operators, casting, control flow, loops,
// arrays, strings, methods, user input, and output formatting.
// ============================================================

public class StudentGradeManager {

    // ============================================
    // Shared "storage" for the whole program
    // Fixed-size arrays simulate a simple database (recap: Arrays)
    // Parallel arrays: index i in each array all describe the SAME student
    // ============================================

    static final int MAX_STUDENTS = 50;          // static + final = shared constant
    static String[] names = new String[MAX_STUDENTS];
    static int[][] scores=new int[MAX_STUDENTS][3];    // 3 subjects per student (2D array)

    static int studentCount = 0;    // tracks how many slots are actually used

    static Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {

        boolean running = true;

        // do-while: menu must show at least once, then loop until user exits
    do{
        printMenu();
        int choice = readMenuChoice();

        // switch expression (modern style) routes to the right method
        switch(choice){
            case 1-> addStudent();
            case 2->viewAllStrudents();
            case 3->searchStudent();
            case 4->classStatistics();
            case 5->{
                System.out.println("Goodbye!");
                running = false;
            }
            default -> System.err.println("Invalid Option. Try again!");
        }
        System.out.println();// spacing between menu cycles

    }while (running);

    scanner.close();
    }

    // ============================================
    // MENU DISPLAY (Output Formatting practice)
    // ============================================

    static void printMenu(){
        System.out.println("=========================================");
        System.out.println("   STUDENT GRADE MANAGEMENT SYSTEM");
        System.out.println("=========================================");
        System.out.println("1. Add Student");
        System.out.println("2. View All Students");
        System.out.println("3. Search Student by Name");
        System.out.println("4. Class Statistics (avg/highest/lowest)");
        System.out.println("5. Exit");
        System.out.print("Choose an option (1-5): ");
    }

    // ============================================
    // SAFE MENU INPUT (User Input + validation, recap of nextInt/hasNextInt gotcha)
    // ============================================
    static int readMenuChoice(){
        if(scanner.hasNextInt()){
            int choice = scanner.nextInt();
            scanner.nextLine(); // consume leftover newline - THE classic fix
            return choice;
        }else {
            scanner.next(); // consume invalid token so it doesn't loop forever
            scanner.nextLine();
            return -1; // signals "invalid" to the switch's default case
        }
    }

    // ============================================
    // ADD STUDENT (Methods, Strings, Arrays, User Input, Control Flow)
    // ============================================

    static void addStudent(){
        if(studentCount>=MAX_STUDENTS){
            System.out.println("Cannot add more students - storage is full.");
            return; // early return - void method exiting early
        }

        System.out.println("Enter student name: ");
        String name = scanner.nextLine().trim();    // String method: trim()

        if(name.isEmpty()){// String method: isEmpty()
            System.out.println("name cannot be empty. Student not added.");
            return;
        }

        int[] subjectScores = new int[3];
        String[] subjects={"Math","Physics","Biology"};

        // for-each loop over subject names, indexed access into subjectScores
        for(int i=0;i<subjects.length;i++){
            subjectScores[i]=readValidScore(subjects[i]);
        }

        names[studentCount]=name;
        scores[studentCount]=subjectScores;
        studentCount++;

        System.out.println("Student '"+name+"' added successfully.");
    }

    // ============================================
    // VALIDATED SCORE INPUT (Loops + Control Flow: keep asking until valid)
    // ============================================

    static int readValidScore(String subjectName){
        int score;

        while(true){// intentional loop, exits only via return below
            System.out.println("Enter "+subjectName+" score (0-100): ");
            if (scanner.hasNextInt()){
                score = scanner.nextInt();
                scanner.nextLine();
                if(score>=0 && score<=100){     //Logic AND
                    return score;
                }else {
                    System.out.println("Score must be between 0 and 100.");
                }
            }else {
                System.out.println("That's not a number.");
                scanner.next();
                scanner.nextLine();
            }

        }
    }

    // ============================================
    // VIEW ALL STUDENTS (Loops, 2D Arrays, printf formatting)
    // ============================================
    static void viewAllStrudents(){
        if(studentCount==0){
            System.out.println("No students recorded yet.");
            return;
        }
        System.out.printf("%-15s %8s %8s %8s %10s%n", "Name", "Math", "Science", "English", "Average");
        System.out.println("-".repeat(55));

        for (int i=0;i<studentCount;i++){
            double average = calculateAverage(scores[i]); // method call, casting inside
            System.out.printf("%-15s %8d %8d %8d %10.2f%n",
                    names[i], scores[i][0], scores[i][1], scores[i][2], average);
        }
    }
    // ============================================
    // CALCULATE AVERAGE (Methods, Casting, Operators)
    // ============================================
    static  double calculateAverage(int[] studentScores){
        int sum=0;

        for(int score:studentScores){   // for-each loop
            sum+=score;     // assignment operator shorthand
        }
        return (double)sum/studentScores.length;    // cast prevents integer division
    }

    // ============================================
    // ASSIGN LETTER GRADE (Control Flow: if-else-if chain)
    // ============================================
    static char assignGrade(double average) {
        if (average >= 90) return 'A';
        else if (average >= 80) return 'B';
        else if (average >= 70) return 'C';
        else if (average >= 60) return 'D';
        else return 'F';
    }

    // ============================================
    // SEARCH STUDENT (Strings: equalsIgnoreCase, Loops, Control Flow)
    // ============================================
    static void searchStudent() {
        if (studentCount == 0) {
            System.out.println("No students to search.");
            return;
        }

        System.out.print("Enter name to search: ");
        String query = scanner.nextLine().trim();

        boolean found = false;
        for (int i = 0; i < studentCount; i++) {
            if (names[i].equalsIgnoreCase(query)) { // case-insensitive String comparison
                double avg = calculateAverage(scores[i]);
                char grade = assignGrade(avg);

                System.out.println("--- Student Found ---");
                System.out.println("Name: " + names[i]);
                System.out.printf("Math: %d | Science: %d | English: %d%n",
                        scores[i][0], scores[i][1], scores[i][2]);
                System.out.printf("Average: %.2f | Grade: %c%n", avg, grade);

                found = true;
                break; // break out of loop once found - no need to keep searching
            }
        }

        if (!found) { // logical NOT
            System.out.println("No student found with that name.");
        }
    }

    // ============================================
    // CLASS STATISTICS (Loops, Arrays, Operators, all rolled together)
    // ============================================
    static void classStatistics() {
        if (studentCount == 0) {
            System.out.println("No students recorded yet.");
            return;
        }

        double totalOfAverages = 0;
        double highestAvg = calculateAverage(scores[0]);
        double lowestAvg = calculateAverage(scores[0]);
        String topStudent = names[0];
        String bottomStudent = names[0];

        for (int i = 0; i < studentCount; i++) {
            double avg = calculateAverage(scores[i]);
            totalOfAverages += avg;

            if (avg > highestAvg) {
                highestAvg = avg;
                topStudent = names[i];
            }
            if (avg < lowestAvg) {
                lowestAvg = avg;
                bottomStudent = names[i];
            }
        }

        double classAverage = totalOfAverages / studentCount;

        System.out.println("--- Class Statistics ---");
        System.out.printf("Total students: %d%n", studentCount);
        System.out.printf("Class average: %.2f (Grade: %c)%n",
                classAverage, assignGrade(classAverage));
        System.out.printf("Top performer: %s (%.2f)%n", topStudent, highestAvg);
        System.out.printf("Needs support: %s (%.2f)%n", bottomStudent, lowestAvg);
    }

}