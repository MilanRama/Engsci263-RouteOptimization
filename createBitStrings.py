def generateBitStrings(bitstrings, n, arr, i):

    '''
    Function that used a recursive loop to generate all bitstrings of length n
    
    Inputs:
        bitstrings - Current list of bitstrings. Generally start with bitstrings = [] (empty list).
        n - Length of bitstrings wanted.
        arr - current bitstring being worked on. Generally start with arr=[0]*n.
        i - current bit index being changed. Generally start with i=0.
    Outputs:
        bitstrings - Outputs currents list of bitstrings. After recursion has finished, this will be all bitstrings of length n.
    '''
    
    if i == n:
        bitstrings.append(arr.copy())
        return
    arr[i] = 0
    generateBitStrings(bitstrings, n, arr, i + 1)
 
    arr[i] = 1
    generateBitStrings(bitstrings, n, arr, i + 1)
    return bitstrings