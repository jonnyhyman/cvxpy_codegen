# CVXPY-CODEGEN FOR WINDOWS

This fork of Nicholas Moehle's cvxpy_codegen is principally intended for use on Windows. There are a number of caveats, but it does work! Read on!

**WARNING:** This tool is still in an early stage of development, and many bugs might still exist.  Consider it an early alpha, and don't use it for safety-critical applications (yet).

CVXPY-CODEGEN generates embedded C code for solving convex optimization problems.  It allows the user to specify a family of convex optimization problems at a high abstraction level using CVXPY in Python, and then solve instances of this problem family in C (possibly on an embedded microcontroller).  The generated C code is essentially a wrapper for embedded optimization solvers (currently only ECOS) for the specified family of problems.

Abstractly, CVXPY-CODEGEN addresses parametrized *families* of convex optimization problems of the form:

    minimize    f_0(x, a)
    subject to  f_i(x, a) <= 0, for i = 1,...,m.

The parameter `a` defines a specific problem instance in the family; for every such problem instance, the variable `x` is to be determined by solving the optimization problem.  In CVXPY-CODEGEN, the problem family (*ie*, the convex functions `f_i`) are specified in Python using CVXPY.  After C code is generated for this family, the user passes in the parameter `a`, and the problem is solved (all in C).  Currently, problems handled include least squares problems, linear programs (LPs), quadratic programs (QPs), second-order cone programs (SOCPs).

# Windows Support Tutorial
Jonny Hyman, 2017                              

 Supports Python 2.7, and C Wrapper does not support Python3
 Tested on Win10/64bit with Anaconda2
 Only supports the ECOS solver

 BEFORE DOING ANYTHING:
  - head into cvxpy_codegen/templates/codegenmodule.c.jinja,
    on line 24, replace #include "your numpy array object path" with your own.
    - later versions may support automatic file finding, but for now its static

 How to go from a CVXPY_CODEGEN problem, to embedded C code, to a Python C Wrapper

0) Installation : Place the egg folder in your Python2 folder... Right now setup.py
    not supported and not needed (?)

1) Write your CVXPY_CODEGEN problem in Python! Recommend that you test in CVXPY,
   then move to CVXPY_CODEGEN when your algorithm is proven stable
     - Note that any dynamic memory assignment within the bound of the problem
       will cause issues, since the generated code in codegen.c and .h have
       fixed array sizes! Complain to Dennis Ritchie!

2) Run the CVXPY_CODEGEN file with prob.codegen('name') at the end
  - The generated files will all compile into your working directory

 CONGRATS! You just made some rad C files which are highly speedy!
 To migrate back into python for a C python wrapper, turn the page!

   #### MSVCRT & VS2015
   The MSVCRT and VS2015 are required to create the C wrapper
   This free Microsoft distribution seems to work for this: https://www.microsoft.com/en-us/download/details.aspx?id=44266

3) Run VS2015 x64 Native Tools Command Prompt (or similar)

4) cd into your working directory

5) "activate (your_anaconda_environment)" [optional]

6) do setup (CHOOSE FROM BELOW)
  6a) python setup.py install <-- makes your new C wrapper available in Python site-packages
  6b) python setup.py build   <-- makes your new C wrapper build locally (./build/...)
  6c) python setup.py clean   <-- cleans out the ./build path if you're recompiling
      - note this doesn't actually seem to work. Recommend manually deleting build folder

7) To call your new wrapper in python (assuming you did 6a or 6b)
   - Ensure all the files related to your package are available
   (in site-packages or in working directory)

   >> import cvxpy_codegen_solver
   >> cvxpy_codegen_solver.cg_solve(each,of,your,input,variables)

 Have fun with your optimizations and make great things!
 Jonny Hyman
 jonnyhyman.com

#### Least squares example
To make this all concrete, let's try a simple least-squares problem:

    import cvxpy_codegen as cg
    m = 10
    n = 5
    A = cg.Parameter(m, n, name='A')
    b = cg.Parameter(m, name='b')
    x = cg.Variable(n, name='x')
    f0 = cg.norm(A*x - b)
    prob = cg.Problem(cg.Minimize(f0))
    prob.codegen('least_squares_example')

Then the generated code is available in the `least_squares_example` directory (which is in the currenty directory).  The API is contained in the header file `codegen.h`.  To test out the embedded solver on randomly generated data, run

    cd ~/least_squares_example
    make
    ./example_problem

If you'd rather not use random data, you can specify the data to be used by adding 

    import numpy as np
    A.value = np.random.randn(m, n)
    b.value = np.random.randn(m, 1)

before generating the C code in Python. (Presumably you would replace the random matrices with whatever values you'd like.)

The directory also contains a Python wrapper, so you can use your embedded C solver in Python as a C extension.  To install this C extension, navigate over to the directory with the generated code, and type `python setup.py install`.  To use it, import it with `import cvxpy_codegen_solver`


#### Optimal control example
As a more sophistocated example, we consider a constrained, linear optimal control problem (such as for model predictive control, or MPC).

    import cvxpy_codegen as cg
    import numpy as np
    np.random.seed(0)
    n = 5
    m = 3
    T = 15

    A  = cg.Parameter(n, n, name='A')
    B  = cg.Parameter(n, m, name='B')
    x0 = cg.Parameter(n, 1, name='x0')

    x = cg.Variable(n, T+1, name='x')
    u = cg.Variable(m, T, name='u')

    obj = 0
    constr = []
    constr += [x[:,0] == x0]
    for t in range(T):
        constr += [x[:,t+1] == A*x[:,t] + B*u[:,t]]
        constr += [cg.norm(u[:,t], 'inf') <= 1] 
        obj += cg.sum_squares(x[:,t+1]) + cg.sum_squares(u[:,t])

    prob = cg.Problem(cg.Minimize(obj), constr)
    prob.codegen('opt_ctrl_example')

#### Installation

To install, clone this repository, `cd` over the directory of the cloned repo, and run `python setup.py install`.  Currently, CVXPY-CODEGEN is not available through any Python repository.  

CVXPY-CODEGEN was only tested in Windows 10, with Python2.7 in an Anaconda2 distribution.

#### Limitations
It is *not* possible (and will never be possible) to change the dimensions of the parameters within a single family of convex problems.

Sparse parameters are not currently supported.

Due to the way CVXPY currently works, it's not possible to use a parameter as the positive semidefinite matrix in the `quad_form` atom. (As a partial fix, we *can* use `sum_squares(L*x)`, using the Cholesky factor `L` as a parameter instead of the positive semidefinite matrix itself.)

#### License
CVXPY-CODEGEN is currently licensed under GPL version 3.  This is because the only supported backend solver, ECOS, is under GPL version 3.  (If you have a different license for ECOS, I'd be more than happy to provide a more permissive license for CVXPY-CODEGEN.)  I am planning on adding at least one more solver, in which case the license for the generated code would have the most permissive license compatible with the chosen backend solver.
