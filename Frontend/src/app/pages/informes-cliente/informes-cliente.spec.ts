import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformesCliente } from './informes-cliente';

describe('InformesCliente', () => {
  let component: InformesCliente;
  let fixture: ComponentFixture<InformesCliente>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InformesCliente],
    }).compileComponents();

    fixture = TestBed.createComponent(InformesCliente);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
