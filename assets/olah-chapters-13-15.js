/* Deterministic teaching demos; no network access or external libraries. */
(() => {
  const activate = (group, selected) => {
    group.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b === selected)));
  };
  const filter = document.querySelector('[data-demo="filter"]');
  if (filter) {
    const output = filter.querySelector('[data-output]');
    filter.querySelectorAll('button[data-id]').forEach(button => button.addEventListener('click', () => {
      const id = Number(button.dataset.id);
      const match = ((id & 0x7F0) === (0x200 & 0x7F0));
      activate(filter.querySelector('[data-choices="id"]'), button);
      output.textContent = '接收 ID 0x' + id.toString(16).toUpperCase().padStart(3,'0') +
        (match ? '：通过过滤器，进入指定 FIFO。' : '：未匹配，被该过滤器拒绝。');
    }));
  }
  const length = document.querySelector('[data-demo="length"]');
  if (length) {
    let meters = 40, rateKbps = 500;
    const output = length.querySelector('[data-output]');
    const render = () => {
      const roundTripNs = 2 * meters * 5;
      const bitNs = 1000000 / rateKbps;
      output.textContent = meters + ' m 主干，' + rateKbps + ' kbit/s：仅线缆往返约 ' +
        roundTripNs + ' ns；单个位时间 ' + bitNs.toFixed(0) +
        ' ns；占位时间约 ' + (100*roundTripNs/bitNs).toFixed(1) + '%（未计收发器与其他时序裕量）。';
    };
    length.querySelectorAll('button[data-length]').forEach(b=>b.addEventListener('click',()=> {
      meters=Number(b.dataset.length); activate(length.querySelector('[data-choices="length"]'),b);render();
    }));
    length.querySelectorAll('button[data-rate]').forEach(b=>b.addEventListener('click',()=> {
      rateKbps=Number(b.dataset.rate); activate(length.querySelector('[data-choices="rate"]'),b);render();
    }));
  }
  const term = document.querySelector('[data-demo="termination"]');
  if (term) {
    const output = term.querySelector('[data-output]');
    term.querySelectorAll('button[data-count]').forEach(b=>b.addEventListener('click',()=> {
      const n=Number(b.dataset.count);
      activate(term.querySelector('[data-choices="count"]'),b);
      output.textContent = n===0 ? '0 个 120 Ω：理想情况下呈开路（∞ Ω）；实测还会受节点内部电路影响。' :
        n + ' 个 120 Ω 并联：理想等效 ' + (120/n).toFixed(n===3?0:0) + ' Ω。' +
        (n===2 ? ' 常见正常断电测量值约为 60 Ω。' : ' 不代表正常端接方式；仍需核对物理位置。');
    }));
  }
})();