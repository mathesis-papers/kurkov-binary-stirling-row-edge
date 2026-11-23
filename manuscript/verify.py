import argparse
from fractions import Fraction
import hashlib
import json
from math import comb, factorial
from pathlib import Path


def digit_product(row_index):
    value = 1
    while row_index:
        value *= 1 + row_index.bit_count()
        row_index //= 2
    return value


def gap_product(row_index):
    positions = [position for position in range(row_index.bit_length())
                 if row_index & (1 << position)]
    weight = len(positions)
    previous = -1
    value = 1
    for offset, position in enumerate(positions):
        value *= (weight - offset + 1) ** (position - previous - 1)
        previous = position
    return value


def literal_rows(max_row, max_column):
    rows = []
    for row_index in range(max_row + 1):
        row = [Fraction(0) for column in range(max_column + 1)]
        row[1] = Fraction(1)
        if row_index == 0:
            row[2] = Fraction(1)
        else:
            parent = rows[row_index // 2]
            for column in range(2, max_column + 1):
                row[column] = column * parent[column] + parent[column - 1]
                if row_index % 2 == 0:
                    row[column] -= (row[column - 1] + parent[column - 1]) / (column - 1)
        rows.append(row)
    return rows


def polynomial_add(first, second):
    length = max(len(first), len(second))
    return tuple((first[index] if index < len(first) else 0)
                 + (second[index] if index < len(second) else 0)
                 for index in range(length))


def polynomial_scale(polynomial, scalar):
    return tuple(coefficient * scalar for coefficient in polynomial)


def polynomial_difference(polynomial):
    result = [0] * len(polynomial)
    for degree, coefficient in enumerate(polynomial):
        for column in range(1, degree + 1):
            result[column] += coefficient * comb(degree, column - 1)
    return tuple(result)


def rising_factorial(degree):
    result = (1,)
    for offset in range(degree):
        result = polynomial_add((0,) + result, polynomial_scale(result, offset))
    return result


def operator_word(row_index, initial=(0, 1), width=None):
    polynomial = initial
    digits = (bin(row_index)[2:] if row_index else '')
    if width is not None:
        digits = digits.zfill(width)
    for digit in digits:
        polynomial = ((0,) + polynomial if digit == '1'
                      else polynomial_difference(polynomial))
    return polynomial


def source_count(max_row):
    values = [1]
    for row_index in range(1, max_row + 1):
        parent = row_index // 2
        value = values[parent]
        if row_index % 2 == 0:
            power = parent & -parent
            value += values[parent - power] + values[row_index - power]
        values.append(value)
    return values


def polynomial_equal(first, second):
    length = max(len(first), len(second))
    return first + (0,) * (length - len(first)) == second + (0,) * (length - len(second))


def sibling_checks(rows):
    counts = {}
    polynomials = [operator_word(row_index) for row_index in range(len(rows))]
    values = source_count(len(rows) - 1)
    rising = [rising_factorial(degree) for degree in range(18)]
    for row_index, row in enumerate(rows):
        weight = row_index.bit_count()
        expansion = (0,)
        for degree in range(1, weight + 3):
            expansion = polynomial_add(expansion, polynomial_scale(
                rising[degree], (-1) ** (weight + 2 - degree) * int(row[degree])))
        assert polynomial_equal(expansion, (0,) + polynomials[row_index])
        falling = (0,)
        for degree in range(1, weight + 3):
            polynomial = tuple(coefficient * (-1) ** (degree - column)
                               for column, coefficient in enumerate(rising[degree]))
            falling = polynomial_add(falling, polynomial_scale(polynomial, int(row[degree])))
        expected_falling = tuple(coefficient * (-1) ** (weight + 1 + column)
                                 for column, coefficient in enumerate(polynomials[row_index]))
        assert polynomial_equal(falling, (0,) + expected_falling)
        assert sum(polynomials[row_index]) == values[row_index]
        minimum = ((row_index + 1) & -(row_index + 1)).bit_length()
        assert all((coefficient > 0) == (minimum <= degree <= weight + 1)
                   for degree, coefficient in enumerate(polynomials[row_index]))
        assert polynomials[row_index][-1] == gap_product(row_index)
        assert values[row_index] >= 2 * gap_product(row_index) - 1
        tail = row_index - (1 << (row_index.bit_length() - 1)) if row_index else 0
        equality = tail & (tail + 1) == 0
        assert (values[row_index] == 2 * gap_product(row_index) - 1) == equality
        subset = row_index
        total = 0
        inverse = 0
        while True:
            total += values[subset]
            inverse += (-1) ** (weight - subset.bit_count()) * digit_product(subset)
            if subset == 0:
                break
            subset = (subset - 1) & row_index
        assert total == digit_product(row_index)
        assert inverse == values[row_index]
        if row_index > 1:
            length = row_index.bit_length() - 1
            assert digit_product(row_index) == 2 * digit_product(tail) + sum(
                digit_product(tail + ((1 << offset) if not tail & (1 << offset) else 0))
                for offset in range(length))
            assert gap_product(row_index) == gap_product(tail) + sum(
                gap_product(tail + (1 << offset)) for offset in range(length)
                if not tail & (1 << offset))
    counts['polynomial_connections'] = len(rows)
    counts['falling_factorial_connections'] = len(rows)
    counts['excedance_recurrence_comparisons'] = len(rows)
    counts['exact_polynomial_support_and_edge'] = len(rows)
    counts['sharp_inequality_and_equality'] = len(rows)
    counts['boolean_transforms'] = 2 * len(rows)
    counts['lower_bit_identities'] = 2 * (len(rows) - 2)
    count = 0
    for parent in range(128):
        for exponent in range(9):
            target = (1 << exponent) * (2 * parent + 1)
            expected = (0,)
            for degree in range(1, parent.bit_count() + 3):
                scalar = ((-1) ** (parent.bit_count() + 2 - degree)
                          * int(rows[parent][degree]) * degree ** exponent)
                expected = polynomial_add(expected, polynomial_scale(rising[degree], scalar))
            assert polynomial_equal(expected, operator_word(target))
            count += 1
    counts['polynomial_blocks_and_signed_factorial_sums'] = count
    count = 0
    generalized = 0
    for parent in range(64):
        for width in range(5):
            for suffix in range(1 << width):
                total = sum(coefficient * sum(operator_word(
                    (1 << width) * ((1 << (degree - 1)) - 1) + suffix))
                    for degree, coefficient in enumerate(polynomials[parent]) if degree)
                assert total == sum(operator_word((1 << width) * parent + suffix))
                count += 1
                if parent:
                    for initial_degree in range(1, 5):
                        initial = rising[initial_degree]
                        prefix = operator_word(parent, initial)
                        total = sum(coefficient * sum(operator_word(
                            (1 << width) * ((1 << (degree - 1)) - 1) + suffix))
                            for degree, coefficient in enumerate(prefix) if degree)
                        target = operator_word((1 << width) * parent + suffix, initial)
                        assert total == sum(target)
                        generalized += 1
    counts['corrected_suffix_identities'] = count
    counts['corrected_generalized_suffix_identities'] = generalized
    count = 0
    for row_index in range(256):
        for initial_degree in range(1, 5):
            polynomial = operator_word(row_index, rising[initial_degree])
            assert sum(polynomial) % factorial(initial_degree) == 0
            if row_index:
                length = row_index.bit_length() - 1
                tail = row_index - (1 << length)
                exponent = length - tail.bit_length()
                expected = polynomial_add(
                    polynomial_scale(operator_word(tail, rising[initial_degree + 1]),
                                     (initial_degree + 1) ** exponent),
                    polynomial_scale(operator_word(tail, rising[initial_degree]),
                                     -initial_degree ** (exponent + 1)))
                assert polynomial_equal(polynomial, expected)
            count += 1
    counts['general_initial_factorial_recurrences'] = count
    assert values[3] == 1
    assert values[1] + 2 * values[2] == 7
    assert factorial(2) == 2
    assert values[0] + values[2] == 4
    counts['explicit_counterexamples'] = 2
    eulerian = [1]
    count = 0
    for width in range(13):
        for weight in range(width + 1):
            total = sum(values[index] for index in range(1 << width)
                        if index.bit_count() == weight)
            assert total == eulerian[weight]
            count += 1
        assert sum(values[:1 << width]) == factorial(width + 1)
        degree = width + 2
        eulerian = [(weight + 1) * (eulerian[weight] if weight < len(eulerian) else 0)
                    + (degree - weight) * (eulerian[weight - 1] if weight else 0)
                    for weight in range(degree)]
    counts['eulerian_weight_sums'] = count
    counts['factorial_row_sums'] = 13
    return {'checks': counts, 'ranges': {
        'all_row_properties': [0, len(rows) - 1],
        'weight_and_factorial_sums_max_width': 12,
        'polynomial_blocks': {'parent': [0, 127], 'exponent': [0, 8]},
        'suffix': {'prefix': [0, 63], 'width': [0, 4], 'suffix': 'all 0 <= q < 2^m'},
        'generalized_suffix': {'prefix': [1, 63], 'initial_degree': [1, 4],
                               'width': [0, 4], 'suffix': 'all 0 <= q < 2^m'},
        'initial_factorial': {'rows': [0, 255], 'initial_degree': [1, 4]}},
        'counterexamples': [
            {'identity': 'unrestricted suffix', 'n': 2, 'm': 0, 'q': 1, 'left': 1, 'right': 7},
            {'identity': 'generalized suffix at zero prefix', 'n': 0, 'k': 2, 'm': 1,
             'q': 0, 'left': 2, 'right': 4}]}


def check():
    max_row = 4095
    max_column = 17
    rows = literal_rows(max_row, max_column)
    counts = {'scalar_entries': 0, 'block_identities': 0, 'edge_identities': 0,
              'gap_products': 0, 'column_two': 0, 'stirling_entries': 0,
              'edge_binomial': 0, 'product_binomial': 0,
              'product_odd_recurrence': 0, 'even_step_recurrences': 0}
    for row_index, row in enumerate(rows):
        edge_column = row_index.bit_count() + 2
        for column, value in enumerate(row):
            assert value.denominator == 1
            assert value >= 0
            assert (value > 0) == (1 <= column <= edge_column)
            counts['scalar_entries'] += 1
        assert row[edge_column] == Fraction(digit_product(row_index), factorial(edge_column - 1))
        counts['edge_identities'] += 1
        assert row[edge_column] == gap_product(row_index)
        counts['gap_products'] += 1
        assert row[2] == 2 * row_index + 1
        counts['column_two'] += 1
        assert digit_product(2 * row_index + 1) == digit_product(row_index) + digit_product(2 * row_index)
        counts['product_odd_recurrence'] += 1
        if row_index:
            exponent = (row_index & -row_index).bit_length() - 1
            shifted_index = 2 * row_index - (1 << exponent)
            assert digit_product(2 * row_index) == digit_product(row_index) + digit_product(shifted_index)
            assert gap_product(2 * row_index) == gap_product(row_index) + gap_product(shifted_index)
            counts['even_step_recurrences'] += 2
            binary_parent = ((row_index >> exponent) - 1) // 2
            for column in range(2, max_column + 1):
                expected = ((column - 1) ** exponent * rows[binary_parent][column - 1]
                            + column ** (exponent + 1) * rows[binary_parent][column])
                assert row[column] == expected
                counts['block_identities'] += 1
    stirling = [[1] + [0] * max_column]
    for degree in range(1, 15):
        previous = stirling[-1]
        stirling.append([0] + [column * previous[column] + previous[column - 1]
                               for column in range(1, max_column + 1)])
    for exponent in range(13):
        row = rows[(1 << exponent) - 1]
        for column in range(1, max_column + 1):
            assert row[column] == stirling[exponent + 2][column]
            counts['stirling_entries'] += 1
    for row_index in range(128):
        for exponent in range(9):
            target = (1 << exponent) * (2 * row_index + 1)
            assert gap_product(target) == sum(comb(exponent, offset) * gap_product((1 << offset) * row_index)
                                              for offset in range(exponent + 1))
            counts['edge_binomial'] += 1
            assert digit_product(target) == sum(comb(exponent + 1, offset) * digit_product((1 << offset) * row_index)
                                                for offset in range(exponent + 2))
            counts['product_binomial'] += 1
    digest = hashlib.sha256()
    for row in rows:
        digest.update((','.join(str(value) for value in row) + '\n').encode())
    return {'status': 'pass', 'arithmetic': 'exact rational and unbounded Python integers',
            'array_range': {'rows': [0, max_row], 'columns': [0, max_column]},
            'binomial_range': {'base_rows': [0, 127], 'exponents': [0, 8]},
            'stirling_range': {'exponents': [0, 12], 'columns': [1, max_column]},
            'checks': counts, 'array_sha256': digest.hexdigest(),
            'siblings': sibling_checks(rows),
            'scope': 'Finite checks of the scalar recurrence and stated identities; all-index arguments are in note.tex.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    text = json.dumps(check(), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
