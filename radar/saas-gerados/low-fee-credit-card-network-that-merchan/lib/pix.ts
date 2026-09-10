/**
 * Gerador de BR Code (Pix Copia e Cola) — padrão EMV QRCPS do Banco Central.
 * Offline: não depende de API, banco ou gateway. Cai direto na conta do recebedor.
 */
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

const campo = (id: string, v: string) => id + String(v.length).padStart(2, "0") + v;

const limpar = (s: string, max: number) =>
  s.normalize("NFD").replace(/[̀-ͯ]/g, "")
   .replace(/[^A-Za-z0-9 .\-]/g, "").trim().slice(0, max).toUpperCase();

export interface DadosPix {
  chave: string;
  nomeRecebedor: string;
  cidade: string;
  valor?: number;
  descricao?: string;
  txid?: string;
}

export function gerarBRCode(d: DadosPix): string {
  const nome = limpar(d.nomeRecebedor || "RECEBEDOR", 25);
  const cidade = limpar(d.cidade || "SAO PAULO", 15);
  const txid = limpar(d.txid || "***", 25) || "***";

  let conta = campo("00", "br.gov.bcb.pix") + campo("01", d.chave);
  if (d.descricao) conta += campo("02", limpar(d.descricao, 40));

  const iniciacao = d.valor && d.valor > 0 && d.txid ? "12" : "11";

  let p = campo("00", "01") + campo("01", iniciacao) + campo("26", conta) +
          campo("52", "0000") + campo("53", "986");
  if (d.valor && d.valor > 0) p += campo("54", d.valor.toFixed(2));
  p += campo("58", "BR") + campo("59", nome) + campo("60", cidade) +
       campo("62", campo("05", txid)) + "6304";

  return p + crc16(p);
}

export function validarBRCode(c: string): boolean {
  return c.length >= 8 && crc16(c.slice(0, -4)) === c.slice(-4).toUpperCase();
}
