import numpy
import scipy.optimize

x = numpy.array([
26,
28,
30,
36,
37,
38,
39,
41,
44,
45,
47,
51,
55,
58,
59,
62,
66,
67
])

y = numpy.array([
514,
549,
585,
688,
705,
722,
739,
772,
820,
836,
868,
931,
992,
1036,
1051,
1095,
1152,
1166,
])

def ratio_curve(x, multiplier, denominator_offset):
    return x * multiplier / (x + denominator_offset)

def power_curve(x, multiplier, power):
    return multiplier * x ** power

def curve_with_offsets(base_function):
    def result(x, x_offset, y_offset, *params):
        #print(x_offset, y_offset, *params)
        return base_function(x + x_offset, *params) + y_offset
    return result

#f, p0, lb, ub
curve_functions = [
    (ratio_curve,
     numpy.array([1.0, 1.0]),
     numpy.array([0.0, 1.0]),
     numpy.array([numpy.inf, numpy.inf]),
     ),
    (power_curve,
     numpy.array([1.0, 1.0]),
     numpy.array([0.0, 0.25]),
     numpy.array([numpy.inf, 4.0]),
     ),
]

for f, p0, lb, ub in curve_functions:
    print(f.__name__)
    popt, pcov = scipy.optimize.curve_fit(f, x, y, p0 = p0, bounds = (lb, ub))
    perr = numpy.sqrt(numpy.diag(pcov))
    print('popt', popt)
    print()

    print(f.__name__, 'with offsets')
    f_with_offsets = curve_with_offsets(f)
    
    p0_offsets = numpy.array([0.0, 0.0])
    p0_with_offsets = numpy.concatenate((p0_offsets, p0))

    max_x = numpy.max(x)
    max_y = numpy.max(y)
    
    lb_offsets = numpy.array([-numpy.inf, 0.0])
    lb_with_offsets = numpy.concatenate((lb_offsets, lb))
    
    ub_offsets = numpy.array([numpy.inf, numpy.inf])
    ub_with_offsets = numpy.concatenate((ub_offsets, ub))
    
    popt, pcov = scipy.optimize.curve_fit(f_with_offsets, x, y,
                                          p0 = p0_with_offsets,
                                          bounds = (lb_with_offsets, ub_with_offsets))
    perr = numpy.sqrt(numpy.diag(pcov))
    print('popt', popt)
    print()
    
