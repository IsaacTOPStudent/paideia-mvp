import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ActivatedRoute } from '@angular/router';

import { StudentsService } from '../../services/students.service';
import { StudentRegister } from '../../interfaces/student-register.interface';

@Component({
  selector: 'app-student-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './student-profile.component.html',
  styleUrl: './student-profile.component.scss'
})
export class StudentProfileComponent implements OnInit {

  private route = inject(ActivatedRoute);
  private studentsService = inject(StudentsService);

  student?: StudentRegister;

  loading = true;
  private cdr = inject(ChangeDetectorRef);
  ngOnInit(): void {

    const id = Number(
      this.route.snapshot.paramMap.get('id')
    );

    console.log('STUDENT ID', id);

    this.studentsService
      .getStudentById(id)
      .subscribe({

      next: (response) => {

  console.log('RESPONSE', response);

  this.student = response;

  console.log('STUDENT ASIGNADO', this.student);

  this.loading = false;

  this.cdr.detectChanges();

},

        error: (error) => {

          console.error(
            'ERROR LOADING STUDENT',
            error
          );

          this.loading = false;

        }

      });

  }

}