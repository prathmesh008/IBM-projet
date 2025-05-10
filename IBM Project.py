import streamlit as st
import google.generativeai as genai
import random
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-pro")
chat = model.start_chat()
response = chat.send_message("Hello!")
print(response.text)


class Product:
    def __init__(self, name, base_price, features):
        self.name = name
        self.base_price = base_price
        self.features = features

class NegotiationChatbot:
    def __init__(self, product, min_discount, max_discount):
        self.product = product
        self.min_discount = min_discount
        self.max_discount = max_discount
        self.current_price = product.base_price
        self.negotiation_rounds = 0
        self.max_rounds = 7
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
        self.competitor_prices = self.generate_competitor_prices()
        self.customer_loyalty = random.randint(1, 5)

    def generate_competitor_prices(self):
        return {
            "Competitor A": round(self.product.base_price * random.uniform(0.9, 1.1), 2),
            "Competitor B": round(self.product.base_price * random.uniform(0.9, 1.1), 2),
        }

    def get_ai_response(self, user_message):
        system_prompt = f"""
        You are an AI salesperson negotiating the price of a {self.product.name}. 
        Current price: ${self.current_price}
        Base price: ${self.product.base_price}
        Features: {', '.join(self.product.features)}
        Competitor prices: {self.competitor_prices}
        Customer loyalty level: {self.customer_loyalty} (1-5 scale)
        Negotiation round: {self.negotiation_rounds + 1} of {self.max_rounds}

        Respond as a salesperson would, highlighting product features and addressing competitor prices if mentioned. 
        Be more fle  Keep your response concise and focused on the negotiation.
        """
        response = self.chat.send_message(f"{system_prompt}\n\nUser: {user_message}")
        return response.text

    def calculate_discount(self, user_offer):
        base_discount = (self.product.base_price - user_offer) / self.product.base_price
        loyalty_factor = self.customer_loyalty / 5
        competitor_factor = 1 - min((user_offer - min(self.competitor_prices.values())) / self.product.base_price, 0.1)
        
        final_discount = base_discount * loyalty_factor * competitor_factor
        return max(min(final_discount, self.max_discount), self.min_discount)

    def negotiate(self, user_offer):
        self.negotiation_rounds += 1
        
        if self.negotiation_rounds > self.max_rounds:
            return f"I apologize, but we've reached our maximum number of negotiation rounds. My final offer stands at ${self.current_price}. Would you like to proceed with this price?"

        if user_offer >= self.current_price:
            return f"Excellent! We have a deal. The {self.product.name} is yours for ${user_offer}. Thank you for your business!"

        if user_offer < self.product.base_price * (1 - self.max_discount):
            return self.get_ai_response(f"The customer offered ${user_offer}, which is significantly below our cost. Explain why we can't go that low and highlight the product's value.")

        discount = self.calculate_discount(user_offer)
        new_price = round(self.product.base_price * (1 - discount), 2)
        self.current_price = max(new_price, self.current_price * 0.95)  # Ensure some price movement

        return self.get_ai_response(f"The customer offered ${user_offer}. Based on our factors, we can offer a price of ${self.current_price}. Respond to the customer, justifying this price.")

def main():
    st.set_page_config(page_title="Advanced AI Negotiation Chatbot", page_icon="💼")
    st.title("Advanced AI Negotiation Chatbot")

    if 'chatbot' not in st.session_state:
        product = Product("High-End Laptop", 1500, ["4K Display", "32GB RAM", "1TB SSD", "Dedicated GPU"])
        st.session_state.chatbot = NegotiationChatbot(product, 0.05, 0.20)
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Welcome! We're discussing our {st.session_state.chatbot.product.name}. "
                       f"It's priced at ${st.session_state.chatbot.current_price} and features "
                       f"{', '.join(st.session_state.chatbot.product.features)}. What's your offer?"
        })

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Your offer or message:")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        try:
            user_offer = float(user_input)
            response = st.session_state.chatbot.negotiate(user_offer)
        except ValueError:
            response = st.session_state.chatbot.get_ai_response(user_input)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

    # Display negotiation information in the sidebar
    st.sidebar.title("Negotiation Info")
    st.sidebar.write(f"Product: {st.session_state.chatbot.product.name}")
    st.sidebar.write(f"Base Price: ${st.session_state.chatbot.product.base_price}")
    st.sidebar.write(f"Current Offer: ${st.session_state.chatbot.current_price}")
    st.sidebar.write(f"Round: {st.session_state.chatbot.negotiation_rounds}/{st.session_state.chatbot.max_rounds}")
    st.sidebar.write("Competitor Prices:")
    for competitor, price in st.session_state.chatbot.competitor_prices.items():
        st.sidebar.write(f"- {competitor}: ${price}")
    st.sidebar.write(f"Customer Loyalty: {st.session_state.chatbot.customer_loyalty}/5")

if __name__ == "__main__":
    main()