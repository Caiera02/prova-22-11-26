"""Agenda de uma sala para um único dia. Execute com Python 3."""
import sys


class Sala:
    def __init__(self, nome):
        self.nome = nome
        self.reservas = {}

    def reservar(self, hora, pessoa):
        if not isinstance(hora, int) or not 0 <= hora <= 23:
            raise ValueError("Digite uma hora inteira entre 0 e 23.")
        if not pessoa.strip():
            raise ValueError("Informe o nome da pessoa.")
        if hora in self.reservas:
            raise ValueError("Este horário já está reservado.")
        self.reservas[hora] = pessoa.strip()

    def cancelar(self, hora):
        if hora not in self.reservas:
            raise ValueError("Nenhuma reserva nesse horário.")
        del self.reservas[hora]

    def listar(self):
        return [f"{hora:02d}h - {self.reservas[hora]}" for hora in sorted(self.reservas)]


def menu():
    sala = Sala("Sala de reunião")
    print(f"{sala.nome} | Agenda do dia")
    while True:
        print("\n1 - Reservar | 2 - Listar | 3 - Cancelar | 0 - Sair")
        opcao = input("Opção: ").strip()
        if opcao == "0":
            break
        if opcao == "2":
            print("\n".join(sala.listar()) or "Agenda vazia.")
        elif opcao in ("1", "3"):
            try:
                hora = int(input("Hora inteira (0 a 23): "))
                if opcao == "1":
                    sala.reservar(hora, input("Nome: "))
                    print("Reserva confirmada.")
                else:
                    sala.cancelar(hora)
                    print("Reserva cancelada.")
            except ValueError as erro:
                print(erro)
        else:
            print("Escolha uma das opções do menu.")


def testar():
    sala = Sala("Teste")
    sala.reservar(14, "Caio")
    assert sala.listar() == ["14h - Caio"]
    try:
        sala.reservar(14, "Ana")
    except ValueError as erro:
        assert str(erro) == "Este horário já está reservado."
    else:
        raise AssertionError("A reserva duplicada deveria ser bloqueada.")
    assert sala.listar() == ["14h - Caio"]
    sala.cancelar(14)
    assert sala.listar() == []
    sala.reservar(14, "Ana")
    assert sala.listar() == ["14h - Ana"]
    print("Testes passaram: reserva, consulta, conflito, cancelamento e reutilização do horário.")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        testar()
    else:
        menu()
