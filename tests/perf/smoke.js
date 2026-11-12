import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'], // SLO: Taxa de erro menor que 1%
    http_req_duration: ['p(95)<200'], // SLO: p95 menor ou igual a 200ms
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://api:8000';

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export default function () {
  const headers = {
    'Content-Type': 'application/json',
  };

  // 1. Healthcheck
  const resHealth = http.get(`${BASE_URL}/health`);
  check(resHealth, {
    'health returns 200': (r) => r.status === 200,
  });

  // 2. Consulta de Empréstimos
  const resList = http.get(`${BASE_URL}/loans`);
  check(resList, {
    'list loans returns 200': (r) => r.status === 200,
  });

  // 3. Criação de Empréstimo
  const bookId = generateUUID();
  const readerId = generateUUID();
  const loanPayload = JSON.stringify({
    book_id: bookId,
    reader_id: readerId,
    borrowed_at: '2026-11-01',
    due_date: '2026-11-08',
  });

  const resCreate = http.post(`${BASE_URL}/loans`, loanPayload, { headers });
  const createOk = check(resCreate, {
    'create loan returns 201': (r) => r.status === 201,
  });

  // 4. Devolução com cálculo de multa
  if (createOk) {
    const loan = JSON.parse(resCreate.body);
    const returnPayload = JSON.stringify({
      returned_at: '2026-11-12',
      policy_type: 'ACADEMIC',
    });

    const resReturn = http.post(`${BASE_URL}/loans/${loan.id}/return`, returnPayload, { headers });
    check(resReturn, {
      'return loan returns 200': (r) => r.status === 200,
    });
  }

  sleep(0.1);
}
