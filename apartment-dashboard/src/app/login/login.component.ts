import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  intro = true;
  resident = false;
  guest = false;
  register1 = false;
  register2 = false;

  constructor() { }

  ngOnInit(): void {
  }


  /**
   * Determines which page is to be displayed next.
   * @param page: the page to navigate to.
   */
  update(page: string): void{
    // Sets which page is to be displayed.
    switch (page) {
      case "resident":
        this.intro = false;
        this.resident = true;
        break;

      case "guest":
        this.intro = false;
        this.guest = true;
        break;

      case "register1":
        this.resident = false;
        this.register1 = true;
        break;

      case "register2":
        this.register1 = false;
        this.register2 = true;
        break;
    }
  }

}
