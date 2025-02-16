import numpy as np

N = 10

def bucket_sort (arr):
    for i in range (1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            if key < arr[j]:
                arr[j+1] = arr[j]
                arr[j] = key
            j-= 1 
    

def bucket_separate(arr):
    n = len(arr)
    a = []
    buckets = [[] for _ in range(n)]
    
    for num in arr:
        bi = int(n * num)
        buckets[bi].append(num)
    
    
    for bucket in buckets:
        bucket_sort(bucket)
    
    ind = 0
    for bucket in buckets:
        for i in bucket:
            arr[ind] = i
            ind += 1
            
    

arr = np.random.rand(N)
print("Tableau trié",arr) 
bucket_separate(arr)
print("Tableau généré",arr)

