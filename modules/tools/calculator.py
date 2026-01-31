"""
Calculator Tool - Perform mathematical calculations
"""

import math
import ast
import operator
from typing import Union
from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus

class Calculator(BaseTool):
    """Safe mathematical calculator"""
    
    # Allowed operations
    ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Allowed functions
    ALLOWED_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pi': math.pi,
        'e': math.e
    }
    
    def __init__(self):
        super().__init__("calculator")
        
    def validate_input(self, expression: str, **kwargs) -> bool:
        """Validate mathematical expression"""
        if not expression or len(expression.strip()) == 0:
            return False
        
        # Check for dangerous operations
        dangerous = ['import', 'exec', 'eval', '__', 'open', 'file']
        for danger in dangerous:
            if danger in expression.lower():
                return False
        
        return True
    
    def _safe_eval(self, node):
        """Safely evaluate AST node"""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._safe_eval(node.left)
            right = self._safe_eval(node.right)
            op = self.ALLOWED_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operation: {type(node.op)}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._safe_eval(node.operand)
            op = self.ALLOWED_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operation: {type(node.op)}")
            return op(operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise ValueError(f"Unsupported function: {func_name}")
            
            args = [self._safe_eval(arg) for arg in node.args]
            return self.ALLOWED_FUNCTIONS[func_name](*args)
        elif isinstance(node, ast.Name):
            if node.id in self.ALLOWED_FUNCTIONS:
                return self.ALLOWED_FUNCTIONS[node.id]
            else:
                raise ValueError(f"Unsupported name: {node.id}")
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")
    
    async def execute(self, expression: str) -> ToolResult:
        """Calculate mathematical expression"""
        
        try:
            # Parse expression
            tree = ast.parse(expression, mode='eval')
            
            # Evaluate safely
            result = self._safe_eval(tree.body)
            
            return ToolResult(
                success=True,
                output=result,
                metadata={
                    'expression': expression,
                    'result_type': type(result).__name__
                }
            )
            
        except ZeroDivisionError:
            return ToolResult(
                success=False,
                output=None,
                error_message="Division by zero",
                status=ToolStatus.FAILURE
            )
        except ValueError as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Invalid expression: {str(e)}",
                status=ToolStatus.FAILURE
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Calculation error: {str(e)}",
                status=ToolStatus.FAILURE
            )
