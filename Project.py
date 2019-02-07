from matplotlib import *
from matplotlib import pyplot

def graph(a,b,x,dx,y,dy,axes):
    z = numpy.arange(numpy.min(x), numpy.max(x) + 1)
    pyplot.figure()
    pyplot.plot(z, a*z+b, color='red')
    pyplot.errorbar(x, y, xerr=dx, yerr=dy, ecolor='blue', fmt='none')
    pyplot.xlabel(axes['x'])
    pyplot.ylabel(axes['y'])
    pyplot.savefig("linear_fit.svg")
    pyplot.show()

def checkRows(input):
    # This function checks if the input files is in a row format
    table = {}
    axes = {}
    endoftable = False
    for line in input.splitlines():
        if line == "":
            endoftable = True
            continue
        if not endoftable:
            entry = line.split()
            key = entry[0].lower()
            somelist = []
            for i in range(1, len(entry)):
                somelist.append(float(entry[i]))
            table[key] = somelist
        else:
            entry = line.split()
            axes[entry[0]] = entry[2] + " " + entry[3]
    length = None
    for v in table.values():
        if length != None and len(v) != length:
            raise ValueError("Input file error: Data lists are not the same length.")
        length = len(v)
    for t in table['dx']:
        if t <= 0:
            raise ValueError("Input file error: Not all uncertainties are positive.")
    return table, axes

def checkColumns(input):
    # This function checks if the input files is in a column format
    table = {}
    axes = {}
    endoftable = False
    isfirst = True
    indexes = []
    for line in input.splitlines():
        if line == "":
            endoftable = True
            continue
        if not endoftable:
            entry = line.split()
            if len(entry) != 4:
                raise ValueError("Input file error: Data lists are not the same length.")
            if isfirst:
                for j in range(len(entry)):
                    indexes.append(entry[j].lower())
                    table[entry[j].lower()] = []
                isfirst = False
            else:
                for j in range(len(entry)):
                    table[indexes[j]].append(float(entry[j]))
        else:
            entry = line.split()
            axes[entry[0]] = entry[2] + " " + entry[3]
    return table, axes

def readinputfile(filename):
    # #This function reads the file and checks which function  to use
    f = open(filename, 'r')
    input = f.read()
    f.close()
    rows = False
    for i in input.splitlines()[0]:
        if i.isdigit():
            rows = True
    if rows:
        return checkRows(input)
    else:
        return checkColumns(input)

def write_results_to_file(filename, a, da, b, db, chi2, chi2_reduced):
    f = open(filename, 'w')
    f.write("a={} +- {}\n".format(a, da))
    f.write("b={} +- {}\n".format(b, db))
    f.write("chi2={}\n".format(chi2))
    f.write("chi2_reduced={}".format(chi2_reduced))
    f.close()

def harmonic_sum(mlist):
    summ=0
    for i in range(len(mlist)):
        summ+=mlist[i]/((table['dy'][i])**2)
    return summ
def harmonic_sum2():
    summ=0
    for i in range(len(table['dy'])):
        summ+=1/((table['dy'][i])**2)
    return summ

def z_roof(mlist):
    return harmonic_sum(mlist)/harmonic_sum2()

def a():
    a=(z_roof([a*b for a,b in zip(table['x'],table['y'])]) -(z_roof(table['x'])*z_roof(table['y'])))/(z_roof([a*b for a,b in zip(table['x'],table['x'])])-z_roof(table['x'])**2)
    return a

def aError():
    s=(z_roof([a*b for a,b in zip(table['dy'],table['dy'])]))/((len(table['dx']))*((z_roof([a*b for a,b in zip(table['x'],table['x'])])-z_roof(table['x'])**2)))
    return s**0.5

def b():
    b=z_roof(table['y']) - a()*z_roof(table['x'])
    return b

def bError():
    s=(z_roof([a*b for a,b in zip(table['dy'],table['dy'])])*z_roof([a*b for a,b in zip(table['x'],table['x'])]))/((len(table['dx']))*((z_roof([a*b for a,b in zip(table['x'],table['x'])])-z_roof(table['x'])**2)))
    return s**0.5

def chi2():
    summ=0
    for i in range(len(table['dx'])):
        summ+=((table['y'][i] - (a()*table['x'][i] + b() ))/table['dy'][i])**2
    return summ

def chi2_reduced(chi2):
    reduced=chi2/(len(table['x']) - 2)
    return reduced

if __name__ == '__main__':
    fileName = input("Please input file name: ")
    table, axes = readinputfile(fileName)
    write_results_to_file('output_txt',a(),aError(),b(),bError(),chi2(),chi2_reduced(chi2()))
    print("a = {} +- {}\n".format(a(), aError()))
    print("b = {} +- {}\n".format(b(), bError()))
    print("chi2 = {}\n".format(chi2()))
    print("chi2_reduced = {}".format(chi2_reduced(chi2())))

    graph(a(), b(), table['x'],table['dx'], table['y'], table['dy'],axes)
