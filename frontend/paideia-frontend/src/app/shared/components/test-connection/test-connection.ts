import { Component, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environments';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-test-connection',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './test-connection.html',
  styleUrls: ['./test-connection.scss'],
})
export class TestConnectionComponent implements OnInit {
    services = signal ([
    { name: 'Auth Service', url: environment.authService, status: 'pending', message: 'Conectando...' },
    { name: 'Student Service', url: environment.studentService, status: 'pending', message: 'Conectando...' },
    { name: 'Diagnostic Service', url: environment.diagnosticService, status: 'pending', message: 'Conectando...' },
    { name: 'Evaluation Service', url: environment.evaluationService, status: 'pending', message: 'Conectando...' },
  ]);

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.testConnections();
  }

  testConnections() {
    this.services().forEach((service, index) => {
      this.http.get(`${service.url}/health/`, { observe: 'response' })
        .subscribe({
          next: (response) => {
            this.updateServiceStatus(index, 'success', `conectado exitosamente ${response.status}`)
          },
          error: (error) => {
            this.updateServiceStatus(index, 'error', `Error ${error.status} || Sin respuesta en puerto`)
          }
        });
    });
  }
  private updateServiceStatus(index: number, status: string, message: string) {
    this.services.update(currentServices => {
      const updated = [...currentServices];
      updated[index] = {...updated[index], status, message};
      return updated
    });
  }
}
