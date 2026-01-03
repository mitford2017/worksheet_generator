#!/usr/bin/env python3
"""
Arithmetic Practice Sheet Generator
Generates professional-looking practice sheets with vertical arithmetic problems
and powers of ten (scientific notation) problems.
Styled like Pearson Education textbook worksheets
"""

import random
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# Unicode superscript digits for exponents
SUPERSCRIPT_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '-': '⁻', '+': '⁺'
}


def to_superscript(num):
    """Convert a number to superscript unicode characters."""
    return ''.join(SUPERSCRIPT_MAP.get(c, c) for c in str(num))


class ArithmeticPracticeGenerator:
    """Generates professional arithmetic practice sheets."""

    def __init__(self, school_name="Lexington Science Academy"):
        self.school_name = school_name
        self.page_width, self.page_height = letter
        self.margin = 0.75 * inch
        self.problems_per_row = 5
        self.rows_per_page = 6

    def generate_problem(self, operation='+', min_val=1, max_val=99,
                         allow_negative_results=False):
        """Generate a single arithmetic problem."""
        if operation == '+':
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            answer = a + b
        elif operation == '-':
            if allow_negative_results:
                a = random.randint(min_val, max_val)
                b = random.randint(min_val, max_val)
            else:
                a = random.randint(min_val, max_val)
                b = random.randint(min_val, a)
            answer = a - b
        elif operation == '*' or operation == '×':
            a = random.randint(min_val, min(max_val, 12))
            b = random.randint(min_val, min(max_val, 12))
            answer = a * b
            operation = '×'
        elif operation == '/' or operation == '÷':
            b = random.randint(max(1, min_val), min(max_val, 12))
            answer = random.randint(min_val, min(max_val, 12))
            a = b * answer
            operation = '÷'
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return {'top': a, 'bottom': b, 'operation': operation, 'answer': answer}

    def generate_powers_of_ten_problem(self, level='intermediate'):
        """
        Generate a powers of ten / scientific notation problem.

        Levels:
        - basic: Simple multiplication/division with powers of 10
                 e.g., 5 × 10³, 2.4 × 10⁻², (3 × 10⁴) × (2 × 10²)
        - intermediate: Two-term operations with scientific notation
                        e.g., (8 × 10⁴) × (2 × 10⁻¹), (6 × 10⁵) ÷ (3 × 10²)
        - advanced: Complex multi-term expressions with division
                    e.g., (8 × 10⁴ × 2 × 10⁻¹) ÷ 16, complex fractions
        """
        if level == 'basic':
            return self._generate_basic_powers_problem()
        elif level == 'intermediate':
            return self._generate_intermediate_powers_problem()
        else:  # advanced
            return self._generate_advanced_powers_problem()

    def _generate_basic_powers_problem(self):
        """Generate basic powers of ten problems."""
        problem_type = random.choice(['single', 'multiply_two'])

        if problem_type == 'single':
            # Simple: coefficient × 10^exp
            coef = random.randint(1, 9)
            exp = random.randint(-3, 6)

            expression = f"{coef} × 10{to_superscript(exp)}"
            answer_val = coef * (10 ** exp)

            # Format answer
            if exp >= 0:
                answer = str(int(answer_val))
            else:
                answer = f"{answer_val:.{abs(exp)}f}".rstrip('0').rstrip('.')

            return {
                'expression': expression,
                'answer': answer,
                'answer_scientific': f"{coef} × 10{to_superscript(exp)}",
                'is_horizontal': True,
                'has_division': False
            }
        else:
            # Multiply two: (a × 10^m) × (b × 10^n)
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            m = random.randint(1, 4)
            n = random.randint(1, 4)

            expression = f"({a} × 10{to_superscript(m)}) × ({b} × 10{to_superscript(n)})"

            # Calculate answer
            result_coef = a * b
            result_exp = m + n

            # Normalize if coefficient >= 10
            if result_coef >= 10:
                result_coef = result_coef / 10
                result_exp += 1

            if result_coef == int(result_coef):
                answer = f"{int(result_coef)} × 10{to_superscript(result_exp)}"
            else:
                answer = f"{result_coef} × 10{to_superscript(result_exp)}"

            return {
                'expression': expression,
                'answer': answer,
                'is_horizontal': True,
                'has_division': False
            }

    def _generate_intermediate_powers_problem(self):
        """Generate intermediate powers of ten problems."""
        problem_type = random.choice(['multiply', 'divide'])

        a = random.randint(2, 9)
        b = random.randint(2, 9)
        m = random.randint(-3, 5)
        n = random.randint(-3, 5)

        if problem_type == 'multiply':
            expression = f"({a} × 10{to_superscript(m)}) × ({b} × 10{to_superscript(n)})"
            result_coef = a * b
            result_exp = m + n
            has_division = False
        else:
            # Ensure clean division
            result = random.randint(2, 9)
            b = random.randint(2, 9)
            a = result * b
            if a > 9:
                a = random.randint(2, 9)
                b = random.choice([c for c in range(1, 10) if a % c == 0])
                result = a // b

            expression = f"({a} × 10{to_superscript(m)}) ÷ ({b} × 10{to_superscript(n)})"
            result_coef = a / b
            result_exp = m - n
            has_division = True

        # Normalize
        while result_coef >= 10:
            result_coef /= 10
            result_exp += 1
        while 0 < result_coef < 1:
            result_coef *= 10
            result_exp -= 1

        if result_coef == int(result_coef):
            answer = f"{int(result_coef)} × 10{to_superscript(result_exp)}"
        else:
            answer = f"{result_coef:.2f}".rstrip('0').rstrip('.') + f" × 10{to_superscript(result_exp)}"

        return {
            'expression': expression,
            'answer': answer,
            'is_horizontal': not has_division,
            'has_division': has_division
        }

    def _generate_advanced_powers_problem(self):
        """Generate advanced powers of ten problems with complex expressions."""
        problem_type = random.choice(['fraction', 'multi_term', 'complex_fraction'])

        if problem_type == 'fraction':
            # (a × 10^m × b × 10^n) ÷ c
            a = random.randint(2, 9)
            b = random.randint(2, 8)
            m = random.randint(2, 6)
            n = random.randint(-3, 3)

            # Choose c to divide evenly
            product = a * b
            divisors = [d for d in range(2, 20) if product % d == 0]
            if divisors:
                c = random.choice(divisors)
            else:
                c = 1

            expression = f"({a} × 10{to_superscript(m)} × {b} × 10{to_superscript(n)}) ÷ {c}"

            result_coef = (a * b) / c
            result_exp = m + n

        elif problem_type == 'multi_term':
            # (a × 10^m) × (b × 10^n) ÷ (c × 10^p)
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            m = random.randint(2, 5)
            n = random.randint(-2, 3)
            p = random.randint(-2, 4)

            product = a * b
            divisors = [d for d in range(2, 10) if product % d == 0]
            c = random.choice(divisors) if divisors else random.randint(2, 5)

            expression = f"({a} × 10{to_superscript(m)}) × ({b} × 10{to_superscript(n)}) ÷ ({c} × 10{to_superscript(p)})"

            result_coef = (a * b) / c
            result_exp = m + n - p

        else:  # complex_fraction - displayed as vertical fraction
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            m = random.randint(3, 6)
            n = random.randint(-2, 3)

            product = a * b
            divisors = [d for d in range(2, 12) if product % d == 0]
            c = random.choice(divisors) if divisors else random.randint(2, 6)
            p = random.randint(1, 4)

            # Numerator and denominator for vertical display
            numerator = f"{a} × 10{to_superscript(m)} × {b} × 10{to_superscript(n)}"
            denominator = f"{c} × 10{to_superscript(p)}"

            expression = {'numerator': numerator, 'denominator': denominator}

            result_coef = (a * b) / c
            result_exp = m + n - p

            # Normalize
            while result_coef >= 10:
                result_coef /= 10
                result_exp += 1
            while 0 < result_coef < 1:
                result_coef *= 10
                result_exp -= 1

            if result_coef == int(result_coef):
                answer = f"{int(result_coef)} × 10{to_superscript(result_exp)}"
            else:
                answer = f"{result_coef:.2f}".rstrip('0').rstrip('.') + f" × 10{to_superscript(result_exp)}"

            return {
                'expression': expression,
                'answer': answer,
                'is_horizontal': False,
                'has_division': True,
                'is_fraction': True
            }

        # Normalize
        while result_coef >= 10:
            result_coef /= 10
            result_exp += 1
        while 0 < result_coef < 1:
            result_coef *= 10
            result_exp -= 1

        if result_coef == int(result_coef):
            answer = f"{int(result_coef)} × 10{to_superscript(result_exp)}"
        else:
            answer = f"{result_coef:.2f}".rstrip('0').rstrip('.') + f" × 10{to_superscript(result_exp)}"

        return {
            'expression': expression,
            'answer': answer,
            'is_horizontal': False,
            'has_division': True,
            'is_fraction': False
        }

    def create_header_footer(self, canvas_obj, doc, page_num, total_pages,
                            worksheet_title, worksheet_subtitle=""):
        """Draw professional header and footer on each page."""
        canvas_obj.saveState()

        # === HEADER ===
        header_y = self.page_height - 0.5 * inch

        # Top decorative line
        canvas_obj.setStrokeColor(colors.HexColor('#1a365d'))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(self.margin, header_y + 0.15*inch,
                       self.page_width - self.margin, header_y + 0.15*inch)

        # School name (left side)
        canvas_obj.setFillColor(colors.HexColor('#1a365d'))
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawString(self.margin, header_y - 0.1*inch, self.school_name)

        # Worksheet title (center)
        canvas_obj.setFont('Helvetica-Bold', 16)
        title_width = canvas_obj.stringWidth(worksheet_title, 'Helvetica-Bold', 16)
        canvas_obj.drawString((self.page_width - title_width) / 2, header_y - 0.1*inch,
                             worksheet_title)

        # Date (right side)
        date_str = datetime.now().strftime("%B %d, %Y")
        canvas_obj.setFont('Helvetica', 10)
        date_width = canvas_obj.stringWidth(date_str, 'Helvetica', 10)
        canvas_obj.drawString(self.page_width - self.margin - date_width,
                             header_y - 0.1*inch, date_str)

        # Subtitle if provided
        if worksheet_subtitle:
            canvas_obj.setFont('Helvetica-Oblique', 10)
            canvas_obj.setFillColor(colors.HexColor('#4a5568'))
            sub_width = canvas_obj.stringWidth(worksheet_subtitle, 'Helvetica-Oblique', 10)
            canvas_obj.drawString((self.page_width - sub_width) / 2,
                                 header_y - 0.35*inch, worksheet_subtitle)

        # Header bottom line
        canvas_obj.setStrokeColor(colors.HexColor('#cbd5e0'))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(self.margin, header_y - 0.5*inch,
                       self.page_width - self.margin, header_y - 0.5*inch)

        # Name and Date fields
        canvas_obj.setFillColor(colors.HexColor('#2d3748'))
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(self.margin, header_y - 0.75*inch, "Name: _______________________________")
        canvas_obj.drawString(self.page_width/2 + 0.5*inch, header_y - 0.75*inch,
                             "Date: ________________    Score: ______ / ______")

        # === FOOTER ===
        footer_y = 0.5 * inch

        # Footer top line
        canvas_obj.setStrokeColor(colors.HexColor('#cbd5e0'))
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(self.margin, footer_y + 0.25*inch,
                       self.page_width - self.margin, footer_y + 0.25*inch)

        # Copyright/Attribution (left)
        canvas_obj.setFillColor(colors.HexColor('#718096'))
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawString(self.margin, footer_y,
                             f"© {datetime.now().year} {self.school_name} | Mathematics Department")

        # Page number (center)
        canvas_obj.setFont('Helvetica-Bold', 10)
        page_text = f"Page {page_num} of {total_pages}"
        page_width = canvas_obj.stringWidth(page_text, 'Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#1a365d'))
        canvas_obj.drawString((self.page_width - page_width) / 2, footer_y, page_text)

        # Practice sheet identifier (right)
        canvas_obj.setFillColor(colors.HexColor('#718096'))
        canvas_obj.setFont('Helvetica', 8)
        sheet_id = f"Worksheet #{random.randint(1000, 9999)}"
        id_width = canvas_obj.stringWidth(sheet_id, 'Helvetica', 8)
        canvas_obj.drawString(self.page_width - self.margin - id_width, footer_y, sheet_id)

        # Bottom decorative line
        canvas_obj.setStrokeColor(colors.HexColor('#1a365d'))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(self.margin, footer_y - 0.15*inch,
                       self.page_width - self.margin, footer_y - 0.15*inch)

        canvas_obj.restoreState()

    def generate_worksheet(self, filename, num_problems=30, operation='+',
                          min_val=1, max_val=99, title=None, subtitle=None,
                          show_answers=False, mixed_operations=False):
        """Generate a complete worksheet PDF for basic arithmetic."""

        # Generate problems
        problems = []
        if mixed_operations:
            ops = ['+', '-', '×', '÷']
            for _ in range(num_problems):
                op = random.choice(ops)
                problems.append(self.generate_problem(op, min_val, max_val))
        else:
            for _ in range(num_problems):
                problems.append(self.generate_problem(operation, min_val, max_val))

        # Setup title
        if title is None:
            op_names = {'+': 'Addition', '-': 'Subtraction', '×': 'Multiplication',
                       '÷': 'Division', '*': 'Multiplication', '/': 'Division'}
            if mixed_operations:
                title = "Mixed Operations Practice"
            else:
                title = f"{op_names.get(operation, 'Arithmetic')} Practice"

        if subtitle is None:
            subtitle = f"Complete all {num_problems} problems. Show your work!"

        # Calculate pages needed
        problems_per_page = self.problems_per_row * self.rows_per_page
        total_pages = (num_problems + problems_per_page - 1) // problems_per_page
        if show_answers:
            total_pages *= 2  # Double for answer key

        # Create PDF
        c = canvas.Canvas(filename, pagesize=letter)

        current_page = 1
        problem_idx = 0

        # Content area dimensions
        content_top = self.page_height - 1.5 * inch
        content_bottom = 1 * inch
        content_left = self.margin
        content_width = self.page_width - 2 * self.margin

        cell_width = content_width / self.problems_per_row
        row_height = (content_top - content_bottom) / self.rows_per_page

        while problem_idx < num_problems:
            # Draw header and footer
            self.create_header_footer(c, None, current_page, total_pages, title, subtitle)

            # Draw problems for this page
            for row in range(self.rows_per_page):
                for col in range(self.problems_per_row):
                    if problem_idx >= num_problems:
                        break

                    prob = problems[problem_idx]
                    x = content_left + col * cell_width + 0.1 * inch
                    y = content_top - (row + 1) * row_height + 0.3 * inch

                    # Draw problem number
                    c.setFillColor(colors.HexColor('#1a365d'))
                    c.setFont('Helvetica-Bold', 9)
                    c.drawString(x, y + 0.55*inch, f"{problem_idx + 1}.")

                    # Draw the vertical problem
                    self._draw_vertical_problem(c, prob, x + 0.25*inch, y, show_answer=False)

                    # Draw box for answer
                    c.setStrokeColor(colors.HexColor('#e2e8f0'))
                    c.setLineWidth(0.5)
                    c.roundRect(x + 0.1*inch, y - 0.35*inch, cell_width - 0.3*inch, 0.3*inch, 3)

                    problem_idx += 1

                if problem_idx >= num_problems:
                    break

            c.showPage()
            current_page += 1

        # Generate answer key if requested
        if show_answers:
            problem_idx = 0
            while problem_idx < num_problems:
                self.create_header_footer(c, None, current_page, total_pages,
                                         f"{title} - ANSWER KEY", "For teacher use only")

                for row in range(self.rows_per_page):
                    for col in range(self.problems_per_row):
                        if problem_idx >= num_problems:
                            break

                        prob = problems[problem_idx]
                        x = content_left + col * cell_width + 0.1 * inch
                        y = content_top - (row + 1) * row_height + 0.3 * inch

                        c.setFillColor(colors.HexColor('#1a365d'))
                        c.setFont('Helvetica-Bold', 9)
                        c.drawString(x, y + 0.55*inch, f"{problem_idx + 1}.")

                        self._draw_vertical_problem(c, prob, x + 0.25*inch, y, show_answer=True)

                        problem_idx += 1

                    if problem_idx >= num_problems:
                        break

                c.showPage()
                current_page += 1

        c.save()
        print(f"Worksheet saved to: {filename}")
        return filename

    def generate_powers_worksheet(self, filename, num_problems=20, level='intermediate',
                                  title=None, subtitle=None, show_answers=False):
        """Generate a powers of ten / scientific notation worksheet."""

        # Generate problems
        problems = []
        for _ in range(num_problems):
            problems.append(self.generate_powers_of_ten_problem(level))

        # Setup title
        if title is None:
            level_titles = {
                'basic': 'Powers of Ten - Basic',
                'intermediate': 'Scientific Notation Practice',
                'advanced': 'Scientific Notation - Advanced'
            }
            title = level_titles.get(level, 'Powers of Ten Practice')

        if subtitle is None:
            subtitle = "Express your answers in scientific notation where appropriate."

        # Layout settings for powers problems (larger cells needed)
        problems_per_row = 2
        rows_per_page = 5
        problems_per_page = problems_per_row * rows_per_page

        total_pages = (num_problems + problems_per_page - 1) // problems_per_page
        if show_answers:
            total_pages *= 2

        # Create PDF
        c = canvas.Canvas(filename, pagesize=letter)

        current_page = 1
        problem_idx = 0

        # Content area dimensions
        content_top = self.page_height - 1.5 * inch
        content_bottom = 1 * inch
        content_left = self.margin
        content_width = self.page_width - 2 * self.margin

        cell_width = content_width / problems_per_row
        row_height = (content_top - content_bottom) / rows_per_page

        while problem_idx < num_problems:
            self.create_header_footer(c, None, current_page, total_pages, title, subtitle)

            for row in range(rows_per_page):
                for col in range(problems_per_row):
                    if problem_idx >= num_problems:
                        break

                    prob = problems[problem_idx]
                    x = content_left + col * cell_width + 0.15 * inch
                    y = content_top - (row + 1) * row_height + 0.4 * inch

                    # Draw problem number
                    c.setFillColor(colors.HexColor('#1a365d'))
                    c.setFont('Helvetica-Bold', 11)
                    c.drawString(x, y + 0.5*inch, f"{problem_idx + 1}.")

                    # Draw the problem
                    self._draw_powers_problem(c, prob, x + 0.3*inch, y, show_answer=False)

                    # Draw answer line
                    c.setStrokeColor(colors.HexColor('#cbd5e0'))
                    c.setLineWidth(1)
                    c.line(x + 0.3*inch, y - 0.35*inch, x + cell_width - 0.4*inch, y - 0.35*inch)
                    c.setFillColor(colors.HexColor('#718096'))
                    c.setFont('Helvetica', 8)
                    c.drawString(x + 0.3*inch, y - 0.5*inch, "Answer:")

                    problem_idx += 1

                if problem_idx >= num_problems:
                    break

            c.showPage()
            current_page += 1

        # Answer key
        if show_answers:
            problem_idx = 0
            while problem_idx < num_problems:
                self.create_header_footer(c, None, current_page, total_pages,
                                         f"{title} - ANSWER KEY", "For teacher use only")

                for row in range(rows_per_page):
                    for col in range(problems_per_row):
                        if problem_idx >= num_problems:
                            break

                        prob = problems[problem_idx]
                        x = content_left + col * cell_width + 0.15 * inch
                        y = content_top - (row + 1) * row_height + 0.4 * inch

                        c.setFillColor(colors.HexColor('#1a365d'))
                        c.setFont('Helvetica-Bold', 11)
                        c.drawString(x, y + 0.5*inch, f"{problem_idx + 1}.")

                        self._draw_powers_problem(c, prob, x + 0.3*inch, y, show_answer=True)

                        problem_idx += 1

                    if problem_idx >= num_problems:
                        break

                c.showPage()
                current_page += 1

        c.save()
        print(f"Powers worksheet saved to: {filename}")
        return filename

    def _draw_vertical_problem(self, canvas_obj, problem, x, y, show_answer=False):
        """Draw a single vertical arithmetic problem on the canvas."""
        top = str(problem['top'])
        bottom = str(problem['bottom'])
        op = problem['operation']
        answer = str(problem['answer'])

        max_len = max(len(top), len(bottom), len(answer))

        # Set font
        canvas_obj.setFont('Courier-Bold', 14)
        canvas_obj.setFillColor(colors.black)

        char_width = 8.4  # Approximate width for Courier-Bold 14

        # Calculate positions for right-alignment
        line_width = (max_len + 1) * char_width + 10

        # Draw top number (right-aligned)
        top_x = x + line_width - len(top) * char_width
        canvas_obj.drawString(top_x, y + 0.35*inch, top)

        # Draw operator and bottom number
        canvas_obj.drawString(x, y + 0.15*inch, op)
        bottom_x = x + line_width - len(bottom) * char_width
        canvas_obj.drawString(bottom_x, y + 0.15*inch, bottom)

        # Draw line
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(1.5)
        canvas_obj.line(x, y + 0.05*inch, x + line_width, y + 0.05*inch)

        # Draw answer if requested
        if show_answer:
            canvas_obj.setFillColor(colors.HexColor('#c53030'))  # Red for answers
            answer_x = x + line_width - len(answer) * char_width
            canvas_obj.drawString(answer_x, y - 0.15*inch, answer)

    def _draw_powers_problem(self, canvas_obj, problem, x, y, show_answer=False):
        """Draw a powers of ten problem on the canvas."""
        expression = problem['expression']
        answer = problem['answer']
        is_fraction = problem.get('is_fraction', False)

        canvas_obj.setFillColor(colors.black)

        if is_fraction and isinstance(expression, dict):
            # Draw as vertical fraction
            numerator = expression['numerator']
            denominator = expression['denominator']

            # Calculate widths
            canvas_obj.setFont('Helvetica', 12)
            num_width = canvas_obj.stringWidth(numerator, 'Helvetica', 12)
            den_width = canvas_obj.stringWidth(denominator, 'Helvetica', 12)
            max_width = max(num_width, den_width) + 20

            # Draw numerator (centered)
            num_x = x + (max_width - num_width) / 2
            canvas_obj.drawString(num_x, y + 0.25*inch, numerator)

            # Draw fraction line
            canvas_obj.setStrokeColor(colors.black)
            canvas_obj.setLineWidth(1.5)
            canvas_obj.line(x, y + 0.1*inch, x + max_width, y + 0.1*inch)

            # Draw denominator (centered)
            den_x = x + (max_width - den_width) / 2
            canvas_obj.drawString(den_x, y - 0.1*inch, denominator)

            # Draw equals and answer if showing
            if show_answer:
                canvas_obj.setFont('Helvetica-Bold', 12)
                canvas_obj.drawString(x + max_width + 10, y + 0.05*inch, "=")
                canvas_obj.setFillColor(colors.HexColor('#c53030'))
                canvas_obj.drawString(x + max_width + 25, y + 0.05*inch, answer)
        else:
            # Draw horizontal expression
            canvas_obj.setFont('Helvetica', 13)
            canvas_obj.drawString(x, y + 0.15*inch, expression)

            # Draw answer if showing
            if show_answer:
                expr_width = canvas_obj.stringWidth(expression, 'Helvetica', 13)
                canvas_obj.setFont('Helvetica-Bold', 13)
                canvas_obj.drawString(x + expr_width + 15, y + 0.15*inch, "=")
                canvas_obj.setFillColor(colors.HexColor('#c53030'))
                canvas_obj.drawString(x + expr_width + 30, y + 0.15*inch, answer)


def main():
    """Example usage of the ArithmeticPracticeGenerator."""
    generator = ArithmeticPracticeGenerator(school_name="Lexington Science Academy")

    print("Generating arithmetic practice worksheets...\n")

    # Addition worksheet
    generator.generate_worksheet(
        filename="addition_practice.pdf",
        num_problems=30,
        operation='+',
        min_val=1,
        max_val=99,
        title="Addition Practice",
        subtitle="Add the numbers. Write your answer below the line.",
        show_answers=True
    )

    # Subtraction worksheet
    generator.generate_worksheet(
        filename="subtraction_practice.pdf",
        num_problems=30,
        operation='-',
        min_val=1,
        max_val=50,
        title="Subtraction Practice",
        subtitle="Subtract the numbers. Write your answer below the line.",
        show_answers=True
    )

    # Multiplication worksheet
    generator.generate_worksheet(
        filename="multiplication_practice.pdf",
        num_problems=30,
        operation='×',
        min_val=2,
        max_val=12,
        title="Multiplication Practice",
        subtitle="Multiply the numbers. Show your work!",
        show_answers=True
    )

    # Division worksheet
    generator.generate_worksheet(
        filename="division_practice.pdf",
        num_problems=30,
        operation='÷',
        min_val=2,
        max_val=12,
        title="Division Practice",
        subtitle="Divide the numbers. All answers are whole numbers.",
        show_answers=True
    )

    # Mixed operations worksheet
    generator.generate_worksheet(
        filename="mixed_operations_practice.pdf",
        num_problems=40,
        mixed_operations=True,
        min_val=2,
        max_val=20,
        title="Mixed Operations Challenge",
        subtitle="Complete each problem. Pay attention to the operation sign!",
        show_answers=True
    )

    # Powers of Ten worksheets
    print("\nGenerating powers of ten worksheets...\n")

    generator.generate_powers_worksheet(
        filename="powers_of_ten_basic.pdf",
        num_problems=20,
        level='basic',
        title="Powers of Ten - Basic",
        subtitle="Simplify each expression. Write answers in standard or scientific notation.",
        show_answers=True
    )

    generator.generate_powers_worksheet(
        filename="powers_of_ten_intermediate.pdf",
        num_problems=16,
        level='intermediate',
        title="Scientific Notation Practice",
        subtitle="Simplify each expression. Express answers in scientific notation.",
        show_answers=True
    )

    generator.generate_powers_worksheet(
        filename="powers_of_ten_advanced.pdf",
        num_problems=12,
        level='advanced',
        title="Scientific Notation - Advanced",
        subtitle="Simplify each expression. Express answers in proper scientific notation.",
        show_answers=True
    )

    print("\nAll worksheets generated successfully!")
    print("\nGenerated files:")
    print("  - addition_practice.pdf")
    print("  - subtraction_practice.pdf")
    print("  - multiplication_practice.pdf")
    print("  - division_practice.pdf")
    print("  - mixed_operations_practice.pdf")
    print("  - powers_of_ten_basic.pdf")
    print("  - powers_of_ten_intermediate.pdf")
    print("  - powers_of_ten_advanced.pdf")


if __name__ == "__main__":
    main()
