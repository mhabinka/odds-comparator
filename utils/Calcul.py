
class Calcul():

    @staticmethod
    def calcul_trj(cote1,coteX,cote2):
        trj = (1 + (1 - (
                    1 / float(cote1) + 1 / float(coteX) + 1 / float(cote2)))) * 100
        return '{0:.2f}'.format(trj)
