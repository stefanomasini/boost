# This function generates all n-bit Gray codes
# Inspired by https://www.geeksforgeeks.org/given-a-number-n-generate-bit-patterns-from-0-to-2n-1-so-that-successive-patterns-differ-by-one-bit/


def generate_gray_codes(n):
    # base case
    if n <= 0:
        return

    # 'arr' will store all generated codes
    # start with one-bit pattern
    arr = ['0', '1']

    # Every iteration of this loop generates 2*i codes from previously generated i codes.
    for iteration_round in range(n-1):
        i = 2 ** (iteration_round+1)

        # Enter the previously generated codes again in arr[] in reverse order.
        # Nor arr[] has double number of codes.
        for j in range(i - 1, -1, -1):
            arr.append(arr[j])

        # append 0 to the first half
        for j in range(i):
            arr[j] = "0" + arr[j]

        # append 1 to the second half
        for j in range(i, 2 * i):
            arr[j] = "1" + arr[j]

    return arr


if __name__ == '__main__':
    codes = generate_gray_codes(5)
    for code in codes:
        print(code)
