class Solution(object):
    def searchMatrix(self, matrix, target):
        """
        :type matrix: List[List[int]]
        :type target: int
        :rtype: bool
        """
        colMax = len(matrix) - 1
        colMin = 0
        rowMax = len(matrix[0]) - 1
        rowMin = 0
        
        colMid = colMax / 2
        colFound = False
        while colMin <= colMax:
            if matrix[colMid][0] <= target <= matrix[colMid][-1]:
                colFound = True
                break
            else:
                if target < matrix[colMid][0]:
                    colMax = colMid - 1
                elif target > matrix[colMid][-1]:
                    colMin = colMid + 1
            colMid = colMin + (colMax - colMin) / 2
            
        print colFound, colMid
        if colFound:
            rowMid = rowMax / 2
            while rowMin <= rowMax:
                if matrix[colMid][rowMid] == target:
                    return True
                else:
                    if matrix[colMid][rowMid] > target:
                        rowMax = rowMid - 1
                    else:
                        rowMin = rowMid + 1
                rowMid = rowMin + (rowMax - rowMin) / 2
            
        else:
            return False
        

sol = Solution()
# x =  [ [1,   3,  5,  7], [10, 11, 16, 20],  [23, 30, 34, 50]]
x = [[1,3]]
sol.searchMatrix(x, 2)
