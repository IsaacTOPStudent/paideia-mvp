import {
  HttpInterceptorFn
} from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {

  const token = localStorage.getItem('access');

  // SI EXISTE TOKEN
  if (token) {

    // CLONAMOS REQUEST
    const clonedReq = req.clone({

      setHeaders: {

        Authorization: `Bearer ${token}`

      }

    });

    return next(clonedReq);

  }

  return next(req);

};