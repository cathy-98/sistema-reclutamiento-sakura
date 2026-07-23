import { AlertTipo, AlertVariante } from '../components/alert/alert';

export interface AlertaUi {
  tipo: AlertTipo;
  variante: AlertVariante;
  mensaje: string;
  titulo?: string;
}

