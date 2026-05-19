import numpy as np
arr = np.array([80,90,70,85])
arr.dtype # int64
arr.shape # (4,)

arr2 = np.array([[1,2,3],[4,5,6]])
arr2.shape # [2][3] 
arr2[0,1] #[0][1]
arr2[:, 0] #[모든행의 0렬]

# Python list: 반복문 필요
[s + 10 for s in [80, 90, 70]]

# numpy: 한 번에 (vectorized operation)
np.array([80, 90, 70]) + 10

import pandas as pd
s = pd.Series([10, 20, 30])
print(s.values)        # numpy array!
print(type(s.values))  # numpy.ndarray