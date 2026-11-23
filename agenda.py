""Agenda local de salas com reservas de uma hora."""
import argparse
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Sala:
    id: int
    nome: str


@dataclass(frozen=True)
class Reserva:
    id: int
    sala_id: int
    responsavel: str
    dia: str
    hora: int

    def resumo(self):
        return f"#{self.id} | {self.dia} às {self.hora:02}h | sala {self.sala_id} | {self.responsavel}"


class Agenda:
    def __init__(self, banco):
        self.banco = banco

    def salas(self):
        return [Sala(*linha) for linha in self.banco.execute("SELECT id, nome FROM sala ORDER BY id")]

    def reservas(self):
        consulta = "SELECT id, sala_id, responsavel, dia, hora FROM reserva ORDER BY dia, hora, sala_id"
        return [Reserva(*linha) for linha in self.banco.execute(consulta)]

    def reservar(self, sala, dia, hora, responsavel):
        if not responsavel.strip():
            raise ValueError("Informe o responsável.")
        if sala not in [item.id for item in self.salas()]:
            raise ValueError("Sala inexistente.")
        try:
            with self.banco:
                cursor = self.banco.execute(
                    "INSERT INTO reserva(sala_id, dia, hora, responsavel) VALUES (?, ?, ?, ?)",
                    (sala, dia.isoformat(), hora, responsavel.strip()),
                )
        except sqlite3.IntegrityError as erro:
            raise ValueError("A sala já está reservada nesse horário.") from erro
        return cursor.lastrowid

    def cancelar(self, codigo):
        with self.banco:
            cursor = self.banco.execute("DELETE FROM reserva WHERE id = ?", (codigo,))
            if not cursor.rowcount:
                raise ValueError("Reserva inexistente.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="acao", required=True)
    comandos.add_parser("salas")
    comandos.add_parser("listar")
    criar = comandos.add_parser("reservar")
    criar.add_argument("sala", type=int)
    criar.add_argument("dia", type=date.fromisoformat)
    criar.add_argument("hora", type=int, choices=range(24))
    criar.add_argument("responsavel")
    comandos.add_parser("cancelar").add_argument("codigo", type=int)
    with sqlite3.connect("agenda.sqlite3") as banco:
        banco.execute("PRAGMA foreign_keys = ON")
        banco.executescript(Path(__file__).with_name("esquema.sql").read_text(encoding="utf-8"))
        agenda = Agenda(banco)
        try:
            args = parser.parse_args()
            if args.acao == "salas":
                for sala in agenda.salas():
                    print(f"{sala.id} | {sala.nome}")
            elif args.acao == "listar":
                print("\n".join(r.resumo() for r in agenda.reservas()) or "Agenda vazia.")
            elif args.acao == "reservar":
                codigo = agenda.reservar(args.sala, args.dia, args.hora, args.responsavel)
                print(f"Reserva #{codigo} confirmada.")
            else:
                agenda.cancelar(args.codigo)
                print("Reserva cancelada.")
        except ValueError as erro:
            parser.exit(1, f"{erro}\n")


if __name__ == "__main__":
    main()
