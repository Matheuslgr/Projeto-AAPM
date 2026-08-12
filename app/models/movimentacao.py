# ============================================================
# models/movimentacao.py — Tabela de movimentações de estoque
# Cada linha representa uma entrada ou saída de um produto.
# O estoque_atual do produto é sempre recalculado a partir
# do histórico de movimentações.

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# ----------------------------------------------------------
# TipoMovimentacao — enum Python espelhado no banco.
# Usar enum evita strings soltas como "entradaa" no banco.
# ----------------------------------------------------------
class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"   # compra, devolução, ajuste positivo
    SAIDA   = "saida"     # venda, perda, ajuste negativo
    # AJUSTE = "ajuste"
    # CANCELAMENTO = "cancelamento"


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id         = Column(Integer, primary_key=True, index=True)

    # ----------------------------------------------------------
    # Tipo da movimentação — usa o enum acima.
    # Armazenado como string no banco ("entrada" / "saida").
    # ----------------------------------------------------------
    tipo       = Column(
        Enum(TipoMovimentacao),
        nullable=False
    )

    quantidade = Column(Integer, nullable=False)

    # Preço unitário no momento da movimentação.
    # Importante registrar pois o preço do produto pode mudar.
    preco_unitario = Column(Float, nullable=False, default=0.0)

    # Motivo opcional — ex: "Compra fornecedor X", "Venda balcão"
    observacao = Column(String(255), nullable=True)

    # Data/hora preenchida automaticamente pelo banco
    criado_em  = Column(DateTime, server_default=func.now())

    # ----------------------------------------------------------
    # Chave estrangeira para o produto movimentado.
    # ondelete="CASCADE" → se o produto for deletado (não apenas
    # desativado), as movimentações dele também são removidas.
    # ----------------------------------------------------------
    produto_id = Column(
        Integer,
        ForeignKey("produtos.id", ondelete="CASCADE"),
        nullable=False
    )

    # Quem registrou a movimentação
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relacionamentos para acessar os objetos completos
    produto = relationship("Produto", backref="movimentacoes")
    usuario = relationship("Usuario", backref="movimentacoes")

   
    @property
    def valor_total(self) -> float:
        """Valor total da movimentação: quantidade × preço unitário."""
        return self.quantidade * self.preco_unitario