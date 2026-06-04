import { Component, inject } from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import { Router } from '@angular/router';

import { StudentsService } from '../../services/students.service';

@Component({
  selector: 'app-student-create',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './student-create.component.html',
  styleUrls: ['./student-create.component.scss']
})

export class StudentCreateComponent {

  private fb = inject(FormBuilder);

  private studentsService = inject(StudentsService);

  private router = inject(Router);

  loading = false;

  studentForm: FormGroup = this.fb.group({

    document_type: ['TI', Validators.required],

    document_number: ['', Validators.required],

    first_name: ['', Validators.required],

    last_name: ['', Validators.required],

    date_of_birth: ['', Validators.required],

    gender: ['', Validators.required],

    grade: ['', Validators.required],

    section: [''],

    guardian_name: ['', Validators.required],

    guardian_phone: ['', Validators.required],

    guardian_email: [''],

    guardian_relationship: [''],

    consent_given: [false, Validators.requiredTrue],

    address: [''],

    neighborhood: [''],

    city: ['Cartagena'],

    socioeconomic_stratum: ['']

  });

  registerStudent() {

    if (this.studentForm.invalid) {

      this.studentForm.markAllAsTouched();

      return;

    }

    this.loading = true;

    console.log(this.studentForm.value);
    console.log(this.studentForm.valid);
    console.log(this.studentForm.errors);

    this.studentsService
      .registerStudent(this.studentForm.value)
      .subscribe({

        next: (response) => {

          console.log('ESTUDIANTE REGISTRADO', response);

          alert('Estudiante registrado exitosamente');

          this.studentForm.reset();

          this.loading = false;

          this.router.navigateByUrl('/students');

        },

        error: (error) => {

          console.error('ERROR REGISTER STUDENT', error);

          alert('Error al registrar estudiante');

          this.loading = false;

        }

      });

  }

}
