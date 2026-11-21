import copy


class HistoricoDesfazer:
    """
    Pilha de estados para Ctrl+Z / Ctrl+Y.

    Guarda o estado *depois* de cada ação; o topo da pilha é o estado atual.
    Desfazer volta ao estado anterior; refazer avança de novo.

    `copiar` e `igual` podem ser trocados para estados que não são dicts
    simples (ex.: imagens do desenho).
    """

    def __init__(self, limite=100, copiar=copy.deepcopy, igual=lambda a, b: a == b):
        self.limite = limite
        self.copiar = copiar
        self.igual = igual
        self.estados = []
        self.refeitos = []

    def reiniciar(self, estado):
        self.estados = [self.copiar(estado)]
        self.refeitos = []

    def registrar(self, estado):
        """Registra o novo estado atual. Devolve False se nada mudou."""
        if self.estados and self.igual(self.estados[-1], estado):
            return False
        self.estados.append(self.copiar(estado))
        self.refeitos = []
        if len(self.estados) > self.limite:
            del self.estados[0]
        return True

    def pode_desfazer(self):
        return len(self.estados) > 1

    def pode_refazer(self):
        return bool(self.refeitos)

    def desfazer(self):
        if not self.pode_desfazer():
            return None
        self.refeitos.append(self.estados.pop())
        return self.copiar(self.estados[-1])

    def refazer(self):
        if not self.refeitos:
            return None
        estado = self.refeitos.pop()
        self.estados.append(estado)
        return self.copiar(estado)
