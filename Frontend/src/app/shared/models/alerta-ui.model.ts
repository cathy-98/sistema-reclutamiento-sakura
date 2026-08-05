import { AlertTipo, AlertVariante } from '../components/alert/alert';

export interface AlertaUi {
  tipo: AlertTipo;
  variante: AlertVariante;
  mensaje: string;
  titulo?: string;
}

export const crearAlerta = (
  tipo: AlertTipo,
  mensaje: string,
  titulo = '',
  variante: AlertVariante = 'soft',
): AlertaUi => ({
  tipo,
  variante,
  mensaje,
  ...(titulo ? { titulo } : {}),
});
