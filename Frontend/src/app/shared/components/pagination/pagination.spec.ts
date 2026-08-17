import '@angular/compiler';
import { describe, expect, it } from 'vitest';

import { Pagination } from './pagination';

describe('Pagination', () => {
  it('muestra todas las paginas cuando hay pocas', () => {
    const component = new Pagination();
    component.total = 30;
    component.pageSize = 5;

    expect(component.pageItems).toEqual([1, 2, 3, 4, 5, 6]);
  });

  it('muestra primera, ultimas, cercanas y elipsis cuando hay muchas paginas', () => {
    const component = new Pagination();
    component.total = 100;
    component.pageSize = 5;
    component.page = 10;

    expect(component.pageItems).toEqual([1, 'ellipsis', 9, 10, 11, 'ellipsis', 20]);
  });

  it('permite emitir salto directo a una pagina', () => {
    const component = new Pagination();
    const emitted: number[] = [];
    component.total = 100;
    component.pageSize = 5;
    component.pageChange.subscribe((page) => emitted.push(page));

    component.changePage(10);

    expect(emitted).toEqual([10]);
  });
});
