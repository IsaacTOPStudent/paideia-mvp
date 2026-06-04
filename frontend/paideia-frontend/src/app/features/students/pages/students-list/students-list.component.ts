import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { StudentsService } from '../../services/students.service';
import { StudentRegister } from '../../interfaces/student-register.interface';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-students-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './students-list.component.html',
  styleUrl: './students-list.component.scss',
})

export class StudentsListComponent implements OnInit {

  private studentsService = inject(StudentsService);

  students: StudentRegister[] = [];

  filteredStudents: StudentRegister[] = [];

  ngOnInit(): void {
    this.loadStudents();
  }

  loadStudents() {

    this.studentsService.getStudents()
      .subscribe({

        next: (response) => {

          console.log('ESTUDIANTES', response);

          this.students = response.data || [];

          this.filteredStudents = [...this.students];

        },

        error: (error) => {

          console.error('ERROR ESTUDIANTES', error);

        }

      });

  }

  filterStudents(event: Event) {

    const value = (event.target as HTMLInputElement)
      .value
      .toLowerCase();

    this.filteredStudents = this.students.filter(student =>
      student.full_name?.toLowerCase().includes(value) ||
      student.document_number?.toLowerCase().includes(value)
    );

  }

}