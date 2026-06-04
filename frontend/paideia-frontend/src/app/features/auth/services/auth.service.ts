import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environments';

@Injectable({
  providedIn: 'root'
})

export class AuthService {

  private http = inject(HttpClient);

  private apiUrl = environment.authService;

  login(email: string, password: string): Observable<any> {

    return this.http.post(`${this.apiUrl}/login/`, {

      email,
      password

    });

  }

}