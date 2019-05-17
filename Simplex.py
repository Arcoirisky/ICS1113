from numpy import array, matrix, transpose, identity, linalg

class Base:

    def __init__ (self, A,b): # Agrear el caso de las Y's
        self.A = A
        self.b = b
        self.m = A.shape[0]
        self.n = A.shape[1]
        self.base = []
        self.Nobase = []
        self.cols = self.sacar_cols('x')

    def sacar_cols(self,name, normal=True):
        if normal: # Agrear el caso de las Y's
            self.valores = []
            cols = {}
            for n in range(self.n):
                cols['{}{}'.format(name,n)] = list(m[n] for m in self.A)
                self.valores.append('{}{}'.format(name,n))
        else:
            cols = []
            for m in range(self.m):
                cols.append(list(n[m] for n in identity(self.m, int)))
        return cols

    def ver_ident(self):
        if len(self.base) == self.m:
            return True
        return False

    def obtener_ident(self):
        ident = self.sacar_cols('I', False)
        for key, value in self.cols.items():
            if value in ident:
                self.base.append(key)

        if not self.ver_ident():
            print("Me faltan variables para tener la base :(")
            return False

        for elem in self.valores:
            if elem not in self.base:
                self.Nobase.append(elem)
        self.sacar_base()

    def sacar_base(self):
        '''
        Aquí tengo y dependo de self.base (ya esta definido y todo)
        Con esto obtengo todas mis matrices (más A y b que ya tenía)

        La idea es que después en Simplex, se cambie self.base para recalcular 
            todo de una.
        '''
        B = []
        for elem in self.base:
            B.append(self.cols[elem])
        self.B = transpose(matrix(B))
        self.NoB = linalg.inv(self.B)
        R = []
        for elem in self.valores:
            if elem in self.Nobase:
                R.append(self.cols[elem])
        self.R = transpose(matrix(R))
        self.NoR = self.NoB * self.R
        self.Nob = self.NoB * self.b
    
class Simplex2:
    def __init__(self, A, b, c):
        self.c = c
        self.A = A
        self.b = b
        self.Nobase = []
        self.bases_ext = Base(self.A, self.b)
        self.bases_ext.obtener_ident()
        self.desempaquetar_bases()
    
    def desempaquetar_bases(self):
        self.vals = self.bases_ext.valores
        self.base = self.bases_ext.base
        self.B = self.bases_ext.B
        self.NoB = self.bases_ext.NoB
        self.R = self.bases_ext.R
        self.NoR = self.bases_ext.NoR
        self.Acols = self.bases_ext.cols
        self.Nob = self.bases_ext.Nob
    
    def separar_c(self):
        c_d = []
        c_b = []
        if len(self.Nobase) == 0:
            for elem in self.vals:
                if elem not in self.base:
                    self.Nobase.append(elem)
        
        for elem in self.Nobase:
            c_d.append(self.c[int(elem[1:])])
        
        for elem in self.base:
            c_b.append(self.c[int(elem[1:])])
        return c_d, c_b

    def minvar(self, entra):
        lista = []
        i = 0
        a_jk = self.Acols[entra]
        print(a_jk)
        print(self.Nob.tolist())
        
        for elem in self.Nob.tolist():
            if a_jk[i] != 0:
                if elem[0]/a_jk[i] > 0:
                    lista.append(elem[0]/a_jk[i])
                else:
                    lista.append(2**90)
            else:
                lista.append(2**90)
            i+=1
        print('listaa', lista)
        sale = self.base[lista.index(min(lista))]
        return sale

    def pVar(self, var):
        letra = var[:1]
        num = int(var[1:]) + 1
        return "{}{}".format(letra,num)

    def negativo_question(self, lista):
        for elem in lista:
            if elem < 0:
                return True
        return False

    def opti(self, lista):
        for elem in lista:
            if elem >= 0:
                return True
        return False

    def reset_bases(self, entra, sale):
        base_1 = [self.pVar(n) for n in self.base]
        print('old base:', ' - '.join(base_1))
        Nobase_1 = [self.pVar(n) for n in self.Nobase]
        print('old no base:', ' - '.join(Nobase_1))
        pos = self.base.index(sale)
        self.base = list(x if (x != sale) else entra for x in self.base)
        base = [self.pVar(n) for n in self.base]
        
        print('new base:', ' - '.join(base))
        self.bases_ext.base = self.base
        pos = self.Nobase.index(entra)
        self.Nobase[pos] = sale
        Nobase = [self.pVar(n) for n in self.Nobase]
        
        print('new No base:',' - '.join(Nobase))
        self.bases_ext.sacar_base()
        self.desempaquetar_bases()
        self.optimo_question()

    def saber_entra(self, costo):
        # Siempre ingresar la variable de costo red neg de menor indice
        # con empate se mete la de menor indice igual
        neg = 0
        copia = []
        i = 0
        for elem in costo:
            if elem < 0:
                neg += 1
                copia.append((i, elem))
            i+= 1
        count = costo.count(min(costo))
        print(count, "AAAAAAAAAAAAAAAAAAAAAAH")
        if count > 1:
            return self.Nobase[sorted(copia)[0][0]]
        else:
            return self.Nobase[costo.index(min(costo))]
        
    def optimo_question(self):
        c_d, c_b = self.separar_c()
        costo = (matrix(c_d) - matrix(c_b)*self.NoR).tolist()[0]
        print(costo)
        if self.negativo_question(costo):
            # Esto es en caso de que no sea el optimo
            entra = self.saber_entra(costo)
            print('entra:', self.pVar(entra))
            sale = self.minvar(entra)
            print('sale:', self.pVar(sale))
            # Ahora se supone que debería modificar la base y repetir
            self.reset_bases(entra, sale)
        else:
            base = [self.pVar(n) for n in self.base]
            print("Finalmente!! U DID IT {", ' , '.join(base),'}')
            return True

if __name__ == '__main__':
    ### Normal
    a = [[2,4,1,0,0],[6,2,0,1,0],[0,1,0,0,1]]
    b = [[1600],[1800],[350]]
    c_x = [-3,-8,0,0,0]
    
    ### Multiple Directo
    #a = [[-1,3,1,0],[2,1,0,1]]
    #b = [[9],[6]]
    #c_x = [-2,-1,0,0]

    ### Multiple Chef
    #a = 
    #b = 
    #c_x = 

    ### Ciclaje 1 -- Lindo
    #a = [[2,1,1,0,0],[0,3,0,1,0],[6,9,0,0,1]]
    #b = [[2], [2], [10]]
    #c_x = [-1,-1,0,0,0]

    ### Deg - Ciclaje -- revisar signo c_x[0]
    #a = [[1,-11,-5,18,1,0,0],[1,-3,-1,2,0,1,0],[1,0,0,0,0,0,1]]
    #b = [[0], [0], [1]]
    #c_x = [10,57,9,24,0,0,0]

    ### Deg -- Aún no lista
    a = [[1/4,-60,-1/25,9,1,0,0],[1/2,-90,-1/50,3,0,1,0],[0,0,1,0,0,0,1]]
    b = [[0],[0],[1]]
    c_x =[-3/4,150,-1/50,0,0,0,0]

    ### Deg -- Aún no lista
    #a = [[1,1,1,0],[-1,1,0,1]]
    #b = [[1],[0]]
    #c_x =[-1,1,0,0]

    A = array(a)
    b = matrix(b)
    c = c_x
    S = Simplex2(A,b,c)
    S.optimo_question()
    