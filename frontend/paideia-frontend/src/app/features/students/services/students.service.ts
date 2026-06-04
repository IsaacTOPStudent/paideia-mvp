import { Injectable, inject } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import { StudentRegister } from '../interfaces/student-register.interface';

import { environment } from '../../../../environments/environments';

@Injectable({
  providedIn: 'root'
})

export class StudentsService {

  private http = inject(HttpClient);

  private apiUrl = `${environment.studentService}/`;

  getStudents(): Observable<any> {

    return this.http.get<any>(this.apiUrl);

  }

  registerStudent(student: StudentRegister) {

    return this.http.post(
      `${this.apiUrl}register/`,
      student
    );

  }
  getStudentById(id: number) {
    return this.http.get<StudentRegister>(
      `${this.apiUrl}${id}/`
    );
  }

}