import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

@Component({
  selector: 'app-error',
  templateUrl: './error.component.html',
  styleUrls: ['./error.component.css']
})
export class ErrorComponent implements OnInit {

  @Input('title') title: string = 'Shit';
  @Input('firstMessage') firstMessage: string = 'I don\'t know what\'s happened' ;
  @Input('secondMessage') secondMessage: string = 'Try to reload the page (may be it will help)';
  @Output('closed') closed = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  onClose() {
    this.closed.emit(null);
  }
}
