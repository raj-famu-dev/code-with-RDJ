#include <stdio.h>
#define MAX_STUDENTS 5
typedef struct { int id; double grade; } Student;
int main(void) {
    Student students[MAX_STUDENTS];
    size_t count = 0;
    printf("How many students (1-%d)? ", MAX_STUDENTS);
    if (scanf("%zu", &count) != 1 || count == 0 || count > MAX_STUDENTS) {
        fputs("Invalid student count.\n", stderr); return 1;
    }
    for (size_t i = 0; i < count; ++i) {
        printf("Enter ID and grade for student %zu: ", i + 1);
        if (scanf("%d %lf", &students[i].id, &students[i].grade) != 2 ||
            students[i].grade < 0.0 || students[i].grade > 100.0) {
            fputs("Invalid record.\n", stderr); return 1;
        }
    }
    FILE *file = fopen("students.txt", "w");
    if (file == NULL) { perror("Could not open students.txt"); return 1; }
    for (size_t i = 0; i < count; ++i) {
        printf("ID: %d | Grade: %.1f\n", students[i].id, students[i].grade);
        if (fprintf(file, "%d,%.1f\n", students[i].id, students[i].grade) < 0) {
            perror("Could not write student record"); fclose(file); return 1;
        }
    }
    if (fclose(file) == EOF) { perror("Could not close students.txt"); return 1; }
    puts("Saved students.txt");
    return 0;
}
