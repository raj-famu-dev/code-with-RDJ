#include <stdio.h>
static double calculate(double a, double b, char op, int *ok) {
    *ok = 1;
    switch (op) {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/': if (b == 0.0) { *ok = 0; return 0.0; } return a / b;
        default: *ok = 0; return 0.0;
    }
}
int main(void) {
    double a = 0.0, b = 0.0;
    char op = '\0';
    int ok = 0;
    printf("Enter: number operator number (example: 12.5 * 2): ");
    if (scanf("%lf %c %lf", &a, &op, &b) != 3) {
        fputs("Invalid input.\n", stderr); return 1;
    }
    double result = calculate(a, b, op, &ok);
    if (!ok) { fputs("Unsupported operation or division by zero.\n", stderr); return 1; }
    printf("Result: %.6g\n", result);
    return 0;
}
