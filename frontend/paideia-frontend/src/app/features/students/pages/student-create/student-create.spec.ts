import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StudentCreate } from './student-create.component';

describe('StudentCreate', () => {
  let component: StudentCreate;
  let fixture: ComponentFixture<StudentCreate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StudentCreate],
    }).compileComponents();

    fixture = TestBed.createComponent(StudentCreate);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
