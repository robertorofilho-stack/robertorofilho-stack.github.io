/**
 * Gerador de BR Code (Pix Copia e Cola) — padrão EMV® QRCPS do Banco Central.
 *
 * 100% offline. Não depende de API, de banco, de gateway nem de credencial.
 * A chave Pix é do recebedor; o código gerado cai direto na conta dele.
 *
 * Referência: Manual de Padrões para Iniciação do Pix (BCB), EMV MPM.
 */

/** CRC16/CCITT-FALSE — polinômio 0x1021, inicial 0xFFFF. Exigido pelo BCB. */
export function crc16(payload: string): string {
  let crc = 0xffff;
  for (let i = 0; i < payload.length; i++) {
    crc ^= payload.charCodeAt(i) << 8;
    for (let b = 0; b < 8; b++) {
      crc = crc & 0x8000 ? ((crc << 1) ^ 0x1021) & 0xffff : (crc << 1) & 0xffff;
    }
  }
  return crc.toString(16).toUpperCase().padStart(4, "0");
}

/** Monta um campo EMV: ID (2) + tamanho (2) + valor. */
function campo(id: string, valor: string): string {
  return id + String(valor.length).padStart(2, "0") + valor;
}

/** Remove acento e caractere fora do permitido pelo padrão. */
function limpar(s: string, max: number): string {
  return s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^A-Za-z0-9 .\-]/g, "")
    .trim()
    .slice(0, max)
    .toUpperCase();
}

export interface DadosPix {
  chave: string;            // e-mail, CPF/CNPJ, telefone (+55...) ou aleatória
  nomeRecebedor: string;    // até 25 caracteres
  cidade: string;           // até 15 caracteres
  valor?: number;           // opcional — sem valor, o pagador digita
  descricao?: string;       // até 40 caracteres
  txid?: string;            // identificador da transação, até 25
}

export function gerarBRCode(d: DadosPix): string {
  const nome = limpar(d.nomeRecebedor || "RECEBEDOR", 25);
  const cidade = limpar(d.cidade || "SAO PAULO", 15);
  const txid = limpar(d.txid || "***", 25) || "***";

  // Conta do recebedor (ID 26)
  let conta = campo("00", "br.gov.bcb.pix") + campo("01", d.chave);
  if (d.descricao) conta += campo("02", limpar(d.descricao, 40));

  // Ponto de iniciação (EMV MPM ID 01):
  //   "11" = estático / reutilizável — mesmo código pago quantas vezes quiser
  //   "12" = dinâmico / uso único — um código por transação
  // Código com valor e txid próprios é de uso único; sem valor, é reutilizável.
  const iniciacao = d.valor && d.valor > 0 && d.txid ? "12" : "11";

  let payload =
    campo("00", "01") +                                  // formato do payload
    campo("01", iniciacao) +                             // estático ou dinâmico
    campo("26", conta) +                                 // conta Pix do recebedor
    campo("52", "0000") +                                // MCC não informado
    campo("53", "986");                                  // moeda: BRL

  if (d.valor && d.valor > 0) {
    payload += campo("54", d.valor.toFixed(2));
  }

  payload +=
    campo("58", "BR") +
    campo("59", nome) +
    campo("60", cidade) +
    campo("62", campo("05", txid));

  payload += "6304";                                     // CRC placeholder
  return payload + crc16(payload);
}

/** Valida um BR Code recalculando o CRC. */
export function validarBRCode(codigo: string): boolean {
  if (codigo.length < 8) return false;
  const corpo = codigo.slice(0, -4);
  const crcInformado = codigo.slice(-4).toUpperCase();
  return crc16(corpo) === crcInformado;
}
