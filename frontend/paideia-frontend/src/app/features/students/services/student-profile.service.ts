import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../../environments/environments';

@Injectable({
  providedIn: 'root'
})
export class StudentProfileService {

  private http = inject(HttpClient);

  getStudent(id: number) {

    return this.http.get(
      `${environment.studentService}/${id}/`
    );

  }

}