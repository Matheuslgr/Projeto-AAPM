# Uma Venda tem um cabeçalho (quem comprou, quando, desconto)
# e N ItensVenda (qual produto, quantos, a que preço).
#
# Separamos em duas tabelas para normalizar os dados —
# o mesmo padrão usado em qualquer sistema comercial real.
# ============================================================

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Venda(Base):
    __tablename__ = "vendas"

    id         = Column(Integer, primary_key=True, index=True)

    # Cliente pode ser NULL — venda para "balcão" sem identificação
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", ondelete="SET NULL"),
        nullable=True
    )

    # Usuário (operador/admin) que registrou a venda
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )

    # Percentual de desconto aplicado — 0.0 ou 10.0 (ou calculado)
    desconto_percentual = Column(Float, nullable=False, default=0.0)
    
    # Desconto manual aplicado na venda
    desconto_manual     = Column(Float, nullable=False, default=0.0)
    desconto_tipo       = Column(String(20), nullable=True, default="reais")  # "reais" ou "porcentagem"

    # Valores calculados e persistidos para histórico imutável
    # (mesmo que o preço do produto mude, a venda permanece correta)
    total_bruto  = Column(Float, nullable=False, default=0.0)
    total_liquido = Column(Float, nullable=False, default=0.0)

    # Observação opcional do operador
    observacao = Column(String(255), nullable=True)

    criado_em = Column(DateTime, server_default=func.now())

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="vendas")
    usuario = relationship("Usuario", backref="vendas")
    itens   = relationship(
        "ItemVenda",
        back_populates="venda",
        cascade="all, delete-orphan"  # deleta itens se a venda for deletada
    )
    pagamentos = relationship(
        "PagamentoVenda",
        back_populates="venda",
        cascade="all, delete-orphan"
    )

    @property
    def desconto_valor(self) -> float:
        """Valor monetário do desconto total aplicado."""
        return max(0.0, round(self.total_bruto - self.total_liquido, 2))

    def __repr__(self):
        return f"<Venda id={self.id} total={self.total_liquido}>"


class PagamentoVenda(Base):
    __tablename__ = "pagamentos_venda"

    id              = Column(Integer, primary_key=True, index=True)
    venda_id        = Column(
        Integer,
        ForeignKey("vendas.id", ondelete="CASCADE"),
        nullable=False
    )
    forma_pagamento = Column(String(50), nullable=False)  # 'DINHEIRO', 'CARTAO_DEBITO', 'CARTAO_CREDITO', 'PIX'
    valor           = Column(Float, nullable=False)       # Valor atribuído à forma de pagamento
    valor_recebido  = Column(Float, nullable=True)        # Caso de dinheiro: valor entregue pelo cliente
    troco           = Column(Float, nullable=True)        # Caso de dinheiro: troco calculado

    venda = relationship("Venda", back_populates="pagamentos")

    def __repr__(self):
        return f"<PagamentoVenda id={self.id} forma={self.forma_pagamento} valor={self.valor}>"


class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id         = Column(Integer, primary_key=True, index=True)

    venda_id   = Column(
        Integer,
        ForeignKey("vendas.id", ondelete="CASCADE"),
        nullable=False
    )

    produto_id = Column(
        Integer,
        ForeignKey("produtos.id", ondelete="SET NULL"),
        nullable=True
    )

    # Dados históricos — não dependem do produto atual no banco
    produto_nome   = Column(String(150), nullable=False)
    quantidade     = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)   # preço no momento da venda

    @property
    def subtotal(self) -> float:
        return self.quantidade * self.preco_unitario

    # Relacionamentos
    venda   = relationship("Venda", back_populates="itens")
    produto = relationship("Produto", backref="itens_venda")