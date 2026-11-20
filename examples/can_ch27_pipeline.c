/* Minimal classic-CAN RX pipeline, no hardware dependency.
   cc -std=c11 -Wall -Wextra -Werror examples/can_ch27_pipeline.c -o /tmp/can27 && /tmp/can27 */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
typedef struct {uint32_t id,timestamp_ms;uint8_t data[8],dlc;bool extended,rtr;} CanFrame;
typedef struct {CanFrame slots[4];unsigned rd,wr,count,lost;} Queue;
typedef struct {float kmh;uint32_t received_ms;} SpeedSample;
static bool enqueue(Queue *q,const CanFrame *f){
    if(q->count==4u){q->lost++;return false;}
    q->slots[q->wr]=*f;q->wr=(q->wr+1u)%4u;q->count++;return true;
}
static bool dequeue(Queue *q,CanFrame *f){
    if(!q->count)return false;
    *f=q->slots[q->rd];q->rd=(q->rd+1u)%4u;q->count--;return true;
}
static bool protocol_decode_speed(const CanFrame *f,SpeedSample *out){
    if(!f||!out||f->id!=0x100u||f->extended||f->rtr||f->dlc<3u||f->dlc>8u)return false;
    uint16_t raw=(uint16_t)f->data[1]|((uint16_t)f->data[2]<<8);
    out->kmh=raw*0.01f;out->received_ms=f->timestamp_ms;return true;
}
static bool fresh(const SpeedSample *s,uint32_t now){
    return s&&(uint32_t)(now-s->received_ms)<=100u; /* short intervals, modulo-safe */
}
int main(void){
    Queue q={0};CanFrame f={.id=0x100u,.timestamp_ms=1000u,.data={0,0x10,0x27},.dlc=3u};
    SpeedSample s={0};
    for(unsigned i=0;i<4u;i++)assert(enqueue(&q,&f));
    assert(!enqueue(&q,&f)&&q.lost==1u);
    assert(dequeue(&q,&f)&&q.count==3u);
    assert(protocol_decode_speed(&f,&s)&&s.kmh>99.99f&&s.kmh<100.01f);
    assert(fresh(&s,1100u)&&!fresh(&s,1101u));
    f.extended=true;assert(!protocol_decode_speed(&f,&s));f.extended=false;
    f.dlc=2u;assert(!protocol_decode_speed(&f,&s));
    f.dlc=3u;f.id=0x101u;assert(!protocol_decode_speed(&f,&s));
    puts("CAN chapter 27 assertions passed");return 0;
}
