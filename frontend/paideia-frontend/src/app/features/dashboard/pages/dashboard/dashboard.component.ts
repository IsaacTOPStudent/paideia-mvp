import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';

import { StudentsService } from '../../../students/services/students.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {

  private studentsService = inject(StudentsService);
  private cdr = inject(ChangeDetectorRef);

  totalStudents = 0;
  activeStudents = 0;
  inactiveStudents = 0;

  recentStudents: any[] = [];

  ngOnInit(): void {

    this.studentsService
      .getStudents()
      .subscribe({

        next: (response) => {

  console.log('DASHBOARD RESPONSE', response);

  const students = response.data;

  console.log('STUDENTS ARRAY', students);

  this.totalStudents = students.length;

  this.activeStudents =
    students.filter(
      (student: any) => student.is_active
    ).length;

  this.inactiveStudents =
    students.filter(
      (student: any) => !student.is_active
    ).length;

  console.log('TOTAL', this.totalStudents);
  console.log('ACTIVOS', this.activeStudents);
  console.log('INACTIVOS', this.inactiveStudents);

  this.recentStudents =
    students.slice(-5).reverse();

  this.cdr.detectChanges();

},
        error: (error) => {

          console.error(
            'ERROR DASHBOARD',
            error
          );

        }

      });

  }

}